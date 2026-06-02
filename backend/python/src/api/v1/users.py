"""Users API router."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserLogin,
    UserPasswordReset,
    UserAgeVerification,
    UserEmailVerify,
    UserPhoneVerify,
)
from src.services.user_service import UserService
from src.middleware.auth import get_current_user
from src.models.user import User

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get user service instance."""
    return UserService(db)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """Create a new user."""
    existing_user = await service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if user_data.username:
        existing_username = await service.get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    user = await service.create_user(user_data)
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current authenticated user information."""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """Get user by ID."""
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Update user by ID."""
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    user = await service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Soft delete user by ID."""
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.get("", response_model=UserListResponse)
async def list_users(
    service: Annotated[UserService, Depends(get_user_service)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = None,
    verification_status: str | None = None,
) -> dict:
    """List all users with pagination."""
    return await service.list_users(
        page=page,
        page_size=page_size,
        status=status,
        verification_status=verification_status,
    )


@router.post("/login", response_model=UserResponse)
async def login(
    login_data: UserLogin,
    service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """Authenticate user and return token."""
    user = await service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return user


@router.post("/verify-age", response_model=UserResponse)
async def verify_age(
    verification_data: UserAgeVerification,
    service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Submit age verification."""
    user = await service.verify_age(current_user.id, verification_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Age verification failed",
        )
    return user


@router.post("/verify-email", response_model=dict)
async def verify_email(
    verification_data: UserEmailVerify,
    service: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    """Verify user email with token."""
    success = await service.verify_email(verification_data.token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    return {"message": "Email verified successfully"}


@router.post("/verify-phone", response_model=dict)
async def verify_phone(
    verification_data: UserPhoneVerify,
    service: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    """Verify user phone with code."""
    success = await service.verify_phone(verification_data.phone, verification_data.code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )
    return {"message": "Phone verified successfully"}


@router.post("/reset-password", response_model=dict)
async def reset_password(
    reset_data: UserPasswordReset,
    service: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    """Reset user password with token."""
    success = await service.reset_password(reset_data.token, reset_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    return {"message": "Password reset successfully"}