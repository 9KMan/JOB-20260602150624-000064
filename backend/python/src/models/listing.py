"""Listing model."""

import enum
import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import String, Boolean, Integer, Text, Numeric, DateTime, Enum, Index, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin


class ListingStatus(enum.Enum):
    """Listing status."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ListingCategory(enum.Enum):
    """Listing category."""

    ADULT_ENTERTAINMENT = "adult_entertainment"
    ESCORT = "escort"
    MASSAGE = "massage"
    COMPANION = "companion"
    DATING = "dating"
    ADULT_CONTENT = "adult_content"
    OTHER = "other"


class Listing(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Listing model representing service listings."""

    __tablename__ = "listings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(250),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    short_description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    category: Mapped[ListingCategory] = mapped_column(
        Enum(ListingCategory),
        nullable=False,
    )
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus),
        default=ListingStatus.DRAFT,
        nullable=False,
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    like_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    review_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    average_rating: Mapped[float | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    price_amount: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    price_currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )
    location_city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    location_state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    location_country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )
    location_lat: Mapped[float | None] = mapped_column(
        Numeric(10, 8),
        nullable=True,
    )
    location_lng: Mapped[float | None] = mapped_column(
        Numeric(11, 8),
        nullable=True,
    )
    contact_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    contact_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    contact_website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    working_hours: Mapped[dict | None] = mapped_column(
        nullable=True,
    )
    images: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(500)),
        nullable=True,
    )
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(50)),
        nullable=True,
    )
    amenities: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(100)),
        nullable=True,
    )
    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="listings",
        foreign_keys=[user_id],
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="listing",
    )

    __table_args__ = (
        Index("ix_listings_user_id_status", "user_id", "status"),
        Index("ix_listings_category_status", "category", "status"),
        Index("ix_listings_location", "location_country", "location_city"),
        Index("ix_listings_slug_lower", "slug", postgresql_using="btree"),
        Index("ix_listings_is_featured_status", "is_featured", "status"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Listing(id={self.id}, title={self.title}, status={self.status})>"


from src.models.user import User
from src.models.payment import Payment