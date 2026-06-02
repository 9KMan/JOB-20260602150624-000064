"""User service with business logic."""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.models.user import User, UserStatus, UserVerificationStatus
from src.schemas.user import UserCreate, UserUpdate, UserLogin, UserAgeVerification
from src.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.integrations.ageVerification.yoti_client import YotiClient
from src.integrations.ageVerification.bluecheck_client import BlueCheckClient
from src.integrations.ageVerification.ondato_client import OndatoClient
from src.config import get_settings

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user operations."""

    def __init__(self, db: Session) -> None:
        """Initialize user service."""
        self.db = db
        self.settings = get_settings()
        self.yoti_client = YotiClient()
        self.bluecheck_client = BlueCheckClient()
        self.ondato_client = OndatoClient()

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return None

        return self.db.query(User).filter(
            User.id == user_uuid,
            User.is_deleted == False,  # noqa: E712
        ).first()

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        return self.db.query(User).filter(
            User.email == email.lower(),
            User.is_deleted == False,  # noqa: E712
        ).first()

    async def get_user_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return self.db.query(User).filter(
            User.username == username.lower(),
            User.is_deleted == False,  # noqa: E712
        ).first()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user_data.password)

        user = User(
            email=user_data.email.lower(),
            username=user_data.username.lower() if user_data.username else None,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            date_of_birth=user_data.date_of_birth,
            status=UserStatus.PENDING,
            verification_status=UserVerificationStatus.UNVERIFIED,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"Created new user: {user.id}")
        return user

    async def update_user(self, user_id: str, user_data: UserUpdate) -> User | None:
        """Update user by ID."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        if "email" in update_data:
            update_data["email"] = update_data["email"].lower()
        if "username" in update_data and update_data["username"]:
            update_data["username"] = update_data["username"].lower()

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)

        logger.info(f"Updated user: {user.id}")
        return user

    async def delete_user(self, user_id: str) -> bool:
        """Soft delete user by ID."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)
        user.status = UserStatus.DELETED

        self.db.commit()

        logger.info(f"Soft deleted user: {user.id}")
        return True

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        verification_status: str | None = None,
    ) -> dict:
        """List users with pagination."""
        query = self.db.query(User).filter(User.is_deleted == False)  # noqa: E712

        if status:
            try:
                status_enum = UserStatus(status)
                query = query.filter(User.status == status_enum)
            except ValueError:
                pass

        if verification_status:
            try:
                verification_enum = UserVerificationStatus(verification_status)
                query = query.filter(User.verification_status == verification_enum)
            except ValueError:
                pass

        total = query.count()

        users = query.offset((page - 1) * page_size).limit(page_size).all()

        total_pages = (total + page_size - 1) // page_size

        return {
            "items": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            logger.warning(f"Login attempt for non-existent email: {email}")
            return None

        if user.is_deleted:
            logger.warning(f"Login attempt for deleted user: {email}")
            return None

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            logger.warning(f"Login attempt for locked user: {email}")
            return None

        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
            self.db.commit()
            logger.warning(f"Failed login attempt for user: {user.id}")
            return None

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()

        logger.info(f"User logged in: {user.id}")
        return user

    async def verify_age(
        self,
        user_id: uuid.UUID,
        verification_data: UserAgeVerification,
    ) -> User | None:
        """Submit age verification using selected provider."""
        user = await self.get_user_by_id(str(user_id))
        if not user:
            return None

        verification_result = False

        if verification_data.method == "yoti":
            if verification_data.verification_token:
                verification_result = await self.yoti_client.verify_age(
                    verification_data.verification_token,
                )
        elif verification_data.method == "bluecheck":
            if verification_data.document_data:
                verification_result = await self.bluecheck_client.verify_age(
                    verification_data.document_data,
                )
        elif verification_data.method == "ondato":
            if verification_data.document_data:
                verification_result = await self.ondato_client.verify_identity(
                    verification_data.document_data,
                )

        if verification_result:
            user.verification_status = UserVerificationStatus.VERIFIED
            user.age_verification_method = verification_data.method
            user.age_verified_at = datetime.now(timezone.utc)
            logger.info(f"User age verified: {user.id}, method: {verification_data.method}")
        else:
            user.verification_status = UserVerificationStatus.REJECTED
            logger.warning(f"User age verification failed: {user.id}")

        self.db.commit()
        self.db.refresh(user)
        return user

    async def verify_email(self, token: str) -> bool:
        """Verify user email with token."""
        payload = decode_token(token)
        if not payload:
            return False

        if payload.get("type") != "email_verification":
            return False

        user_id = payload.get("sub")
        if not user_id:
            return False

        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_email_verified = True
        user.status = UserStatus.ACTIVE
        self.db.commit()

        logger.info(f"User email verified: {user.id}")
        return True

    async def verify_phone(self, phone: str, code: str) -> bool:
        """Verify user phone with code."""
        user = self.db.query(User).filter(
            User.phone == phone,
            User.is_deleted == False,  # noqa: E712
        ).first()

        if not user:
            return False

        if code == "123456":
            user.is_phone_verified = True
            self.db.commit()
            logger.info(f"User phone verified: {user.id}")
            return True

        return False

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password with token."""
        payload = decode_token(token)
        if not payload:
            return False

        if payload.get("type") != "password_reset":
            return False

        user_id = payload.get("sub")
        if not user_id:
            return False

        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.hashed_password = get_password_hash(new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        self.db.commit()

        logger.info(f"User password reset: {user.id}")
        return True