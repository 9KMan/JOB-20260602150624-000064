"""Listing Pydantic schemas."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator
import re


class ListingBase(BaseModel):
    """Base listing schema."""

    title: Annotated[str, Field(min_length=10, max_length=200)]
    description: Annotated[str, Field(min_length=50, max_length=5000)]
    short_description: str | None = Field(default=None, max_length=500)
    category: str
    price_amount: float | None = Field(default=None, ge=0)
    price_currency: str = Field(default="USD", max_length=3)
    location_city: str | None = Field(default=None, max_length=100)
    location_state: str | None = Field(default=None, max_length=100)
    location_country: Annotated[str, Field(max_length=2)]
    location_lat: float | None = None
    location_lng: float | None = None
    contact_phone: str | None = Field(default=None, max_length=20)
    contact_email: str | None = None
    contact_website: str | None = None
    tags: list[str] | None = None
    amenities: list[str] | None = None


class ListingCreate(ListingBase):
    """Schema for creating a listing."""

    working_hours: dict | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title format."""
        if not re.match(r"^[a-zA-Z0-9\s\-_.,!?]+$", v):
            raise ValueError("Title contains invalid characters")
        return v

    @field_validator("contact_email")
    @classmethod
    def validate_contact_email(cls, v: str | None) -> str | None:
        """Validate contact email."""
        if v is not None:
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
                raise ValueError("Invalid contact email format")
        return v


class ListingUpdate(BaseModel):
    """Schema for updating a listing."""

    title: str | None = Field(default=None, min_length=10, max_length=200)
    description: str | None = Field(default=None, min_length=50, max_length=5000)
    short_description: str | None = Field(default=None, max_length=500)
    price_amount: float | None = Field(default=None, ge=0)
    price_currency: str | None = Field(default=None, max_length=3)
    location_city: str | None = Field(default=None, max_length=100)
    location_state: str | None = Field(default=None, max_length=100)
    location_country: str | None = Field(default=None, max_length=2)
    location_lat: float | None = None
    location_lng: float | None = None
    contact_phone: str | None = Field(default=None, max_length=20)
    contact_email: str | None = None
    contact_website: str | None = None
    working_hours: dict | None = None
    tags: list[str] | None = None
    amenities: list[str] | None = None
    images: list[str] | None = None
    status: str | None = None


class ListingResponse(BaseModel):
    """Schema for listing response."""

    id: datetime
    user_id: datetime
    title: str
    slug: str
    description: str
    short_description: str | None = None
    category: str
    status: str
    is_featured: bool
    is_premium: bool
    is_verified: bool
    view_count: int
    like_count: int
    review_count: int
    average_rating: float | None = None
    price_amount: float | None = None
    price_currency: str
    location_city: str | None = None
    location_state: str | None = None
    location_country: str
    location_lat: float | None = None
    location_lng: float | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    contact_website: str | None = None
    working_hours: dict | None = None
    images: list[str] | None = None
    tags: list[str] | None = None
    amenities: list[str] | None = None
    rejection_reason: str | None = None
    expires_at: datetime | None = None
    activated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ListingListResponse(BaseModel):
    """Schema for paginated listing list response."""

    items: list[ListingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ListingSearchQuery(BaseModel):
    """Schema for listing search query."""

    query: str | None = None
    category: str | None = None
    location_country: str | None = None
    location_city: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    is_verified: bool | None = None
    is_premium: bool | None = None
    sort_by: str = Field(default="created_at", pattern=r"^(created_at|price|rating|popular)$")
    sort_order: str = Field(default="desc", pattern=r"^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ListingStatusUpdate(BaseModel):
    """Schema for updating listing status."""

    status: str
    rejection_reason: str | None = None