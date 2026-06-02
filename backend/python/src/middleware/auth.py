"""JWT authentication middleware."""

import logging
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from src.config import get_settings
from src.database import get_db
from src.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Middleware for JWT authentication."""

    def __init__(self) -> None:
        """Initialize auth middleware."""
        self.settings = get_settings()

    async def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify JWT token.

        Args:
            token: JWT token string

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            if self.settings.auth.auth0_domain:
                payload = await self._verify_auth0_token(token)
            else:
                payload = jwt.decode(
                    token,
                    self.settings.auth.jwt_secret_key,
                    algorithms=[self.settings.auth.jwt_algorithm],
                )

            return payload

        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    async def _verify_auth0_token(self, token: str) -> dict[str, Any]:
        """Verify Auth0 token.

        Args:
            token: Auth0 token

        Returns:
            Token payload
        """
        jwks_url = f"https://{self.settings.auth.auth0_domain}/.well-known/jwks.json"

        payload = jwt.decode(
            token,
            key={"kty": "RSA"},
            algorithms=self.settings.auth.auth0_algorithms,
            audience=self.settings.auth.auth0_audience,
            domain=self.settings.auth.auth0_domain,
        )

        return payload


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        Authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_middleware = AuthMiddleware()
    payload = await auth_middleware.verify_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_uuid).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User | None:
    """Get current user if authenticated, None otherwise.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User if authenticated, None otherwise
    """
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None