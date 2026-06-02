"""Input validation utilities."""

import re
from typing import Any


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email string to validate

    Returns:
        True if valid email format
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format.

    Args:
        phone: Phone string to validate

    Returns:
        True if valid phone format
    """
    pattern = r"^\+?[1-9]\d{1,14}$"
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    return bool(re.match(pattern, cleaned))


def validate_url(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL format
    """
    pattern = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
    return bool(re.match(pattern, url))


def validate_slug(slug: str) -> bool:
    """Validate URL slug format.

    Args:
        slug: Slug string to validate

    Returns:
        True if valid slug format
    """
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    return bool(re.match(pattern, slug))


def validate_password_strength(password: str) -> dict[str, Any]:
    """Validate password strength.

    Args:
        password: Password string to validate

    Returns:
        Dictionary with validation result and errors
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def validate_username(username: str) -> bool:
    """Validate username format.

    Args:
        username: Username string to validate

    Returns:
        True if valid username format
    """
    if len(username) < 3 or len(username) > 30:
        return False

    pattern = r"^[a-zA-Z0-9_]+$"
    return bool(re.match(pattern, username))


def sanitize_input(text: str) -> str:
    """Sanitize user input by removing potentially dangerous characters.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text
    """
    text = re.sub(r"[<>]", "", text)
    text = text.strip()
    return text


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format.

    Args:
        uuid_string: UUID string to validate

    Returns:
        True if valid UUID format
    """
    import uuid

    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False