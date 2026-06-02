"""Security utilities for password hashing and JWT tokens."""

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored password hash

    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: str,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Create a JWT access token.

    Args:
        user_id: User ID to encode in token
        expires_delta: Optional custom expiration time
        additional_claims: Optional additional claims to include

    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.auth.jwt_access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(
        payload,
        settings.auth.jwt_secret_key,
        algorithm=settings.auth.jwt_algorithm,
    )

    return token


def create_refresh_token(
    user_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token.

    Args:
        user_id: User ID to encode in token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.auth.jwt_refresh_token_expire_days)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    token = jwt.encode(
        payload,
        settings.auth.jwt_secret_key,
        algorithm=settings.auth.jwt_algorithm,
    )

    return token


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.auth.jwt_secret_key,
            algorithms=[settings.auth.jwt_algorithm],
        )
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.JWTClaimsError:
        logger.warning("Invalid token claims")
        return None
    except jwt.JWTError:
        logger.warning("Invalid token")
        return None
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        return None


def create_email_verification_token(user_id: str) -> str:
    """Create an email verification token.

    Args:
        user_id: User ID

    Returns:
        Verification token
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=24)

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "email_verification",
    }

    return jwt.encode(
        payload,
        settings.auth.jwt_secret_key,
        algorithm=settings.auth.jwt_algorithm,
    )


def create_password_reset_token(user_id: str) -> str:
    """Create a password reset token.

    Args:
        user_id: User ID

    Returns:
        Password reset token
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "password_reset",
    }

    return jwt.encode(
        payload,
        settings.auth.jwt_secret_key,
        algorithm=settings.auth.jwt_algorithm,
    )


def generate_random_token(length: int = 32) -> str:
    """Generate a random token.

    Args:
        length: Token length in bytes (output will be hex, so 2x length)

    Returns:
        Random hex token
    """
    import secrets
    return secrets.token_hex(length)