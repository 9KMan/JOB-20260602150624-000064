"""User Pydantic schemas."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
import re


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str | None = Field(default=None, max_length=100, pattern=r"^[a-zA-Z0-9_]+$")
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: Annotated[str, Field(min_length=8, max_length=128)]
    date_of_birth: datetime | None = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    username: str | None = Field(default=None, max_length=100, pattern=r"^[a-zA-Z0-9_]+$")
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    avatar_url: str | None = None
    date_of_birth: datetime | None = None


class UserResponse(BaseModel):
    """Schema for user response."""

    id: datetime
    email: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    status: str
    is_email_verified: bool
    is_phone_verified: bool
    verification_status: str
    date_of_birth: datetime | None = None
    age_verified_at: datetime | None = None
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserPasswordReset(BaseModel):
    """Schema for password reset."""

    token: str
    new_password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserAgeVerification(BaseModel):
    """Schema for age verification request."""

    method: str = Field(description="Verification method: yoti, bluecheck, ondato")
    verification_token: str | None = None
    document_data: dict | None = None


class UserEmailVerify(BaseModel):
    """Schema for email verification."""

    token: str


class UserPhoneVerify(BaseModel):
    """Schema for phone verification."""

    phone: str
    code: str