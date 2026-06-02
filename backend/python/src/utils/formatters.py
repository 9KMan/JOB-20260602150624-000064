"""Response formatting utilities."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Any


def format_phone_number(phone: str, country_code: str = "US") -> str:
    """Format phone number for display.

    Args:
        phone: Raw phone number
        country_code: ISO country code

    Returns:
        Formatted phone number
    """
    digits = re.sub(r"\D", "", phone)

    if country_code == "US" and len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}"

    if country_code == "US" and len(digits) == 11 and digits[0] == "1":
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

    return phone


def format_currency(
    amount: Decimal | float,
    currency: str = "USD",
    include_symbol: bool = True,
) -> str:
    """Format amount as currency string.

    Args:
        amount: Amount to format
        currency: Currency code
        include_symbol: Whether to include currency symbol

    Returns:
        Formatted currency string
    """
    amount_float = float(amount)

    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "CAD": "C$",
        "AUD": "A$",
    }

    formatted = f"{amount_float:,.2f}"

    if include_symbol and currency in symbols:
        return f"{symbols[currency]}{formatted}"

    return f"{formatted} {currency}"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)].rstrip() + suffix


def format_datetime(
    dt: datetime,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    include_timezone: bool = False,
) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime to format
        format_str: strftime format string
        include_timezone: Whether to include timezone

    Returns:
        Formatted datetime string
    """
    formatted = dt.strftime(format_str)

    if include_timezone:
        formatted += f" {dt.strftime('%z')}"

    return formatted


def format_listing_title(title: str, category: str | None = None) -> str:
    """Format listing title for display.

    Args:
        title: Raw listing title
        category: Optional category

    Returns:
        Formatted title
    """
    title = title.strip()
    title = re.sub(r"\s+", " ", title)

    if category:
        category_labels = {
            "adult_entertainment": "Adult Entertainment",
            "escort": "Escort",
            "massage": "Massage",
            "companion": "Companion",
            "dating": "Dating",
            "adult_content": "Adult Content",
        }
        category_label = category_labels.get(category, category.title())
        return f"{category_label}: {title}"

    return title


def format_user_display_name(
    first_name: str | None,
    last_name: str | None,
    username: str | None,
    email: str | None,
) -> str:
    """Format user display name.

    Args:
        first_name: User first name
        last_name: User last name
        username: User username
        email: User email

    Returns:
        Formatted display name
    """
    if first_name and last_name:
        return f"{first_name} {last_name}"

    if first_name:
        return first_name

    if username:
        return username

    if email:
        return email.split("@")[0]

    return "Anonymous"


def format_api_response(
    data: Any,
    message: str | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Format standardized API response.

    Args:
        data: Response data
        message: Optional message
        meta: Optional metadata

    Returns:
        Formatted response dictionary
    """
    response: dict[str, Any] = {"data": data}

    if message:
        response["message"] = message

    if meta:
        response["meta"] = meta

    return response


def format_pagination_meta(
    page: int,
    page_size: int,
    total: int,
    total_pages: int,
) -> dict[str, Any]:
    """Format pagination metadata.

    Args:
        page: Current page
        page_size: Items per page
        total: Total items
        total_pages: Total pages

    Returns:
        Pagination metadata
    """
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }