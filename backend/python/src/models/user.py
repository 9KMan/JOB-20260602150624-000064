"""User model."""

import enum
import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import String, Boolean, DateTime, Enum, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin


class UserStatus(enum.Enum):
    """User account status."""

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class UserVerificationStatus(enum.Enum):
    """User age/identity verification status."""

    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """User model representing platform users."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus),
        default=UserStatus.PENDING,
        nullable=False,
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_phone_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    verification_status: Mapped[UserVerificationStatus] = mapped_column(
        Enum(UserVerificationStatus),
        default=UserVerificationStatus.UNVERIFIED,
        nullable=False,
    )
    date_of_birth: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    age_verification_method: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    age_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    listings: Mapped[list["Listing"]] = relationship(
        "Listing",
        back_populates="user",
        foreign_keys="Listing.user_id",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="user",
    )

    __table_args__ = (
        Index("ix_users_email_lower", "email", postgresql_using="btree"),
        Index("ix_users_status_is_deleted", "status", "is_deleted"),
        Index("ix_users_verification_status", "verification_status"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, email={self.email}, status={self.status})>"


from src.models.listing import Listing
from src.models.payment import Payment