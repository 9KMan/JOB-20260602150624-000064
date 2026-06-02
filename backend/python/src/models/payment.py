"""Payment models."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import String, Boolean, Integer, Numeric, DateTime, Enum, Index, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import UUIDMixin, TimestampMixin


class PaymentStatus(enum.Enum):
    """Payment status."""

    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    VOIDED = "voided"
    EXPIRED = "expired"


class PaymentMethod(enum.Enum):
    """Payment method type."""

    CCBILL = "ccbill"
    PAXUM = "paxum"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    OTHER = "other"


class PaymentType(enum.Enum):
    """Payment type."""

    SUBSCRIPTION = "subscription"
    LISTING_PROMOTION = "listing_promotion"
    VERIFICATION = "verification"
    OTHER = "other"


class Payment(Base, UUIDMixin, TimestampMixin):
    """Payment model."""

    __tablename__ = "payments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    listing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod),
        nullable=False,
    )
    payment_type: Mapped[PaymentType] = mapped_column(
        Enum(PaymentType),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )
    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )
    provider_response: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    refunded_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    is_test: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="payments",
    )
    listing: Mapped["Listing"] = relationship(
        "Listing",
        back_populates="payments",
    )
    transactions: Mapped[list["PaymentTransaction"]] = relationship(
        "PaymentTransaction",
        back_populates="payment",
        order_by="PaymentTransaction.created_at",
    )

    __table_args__ = (
        Index("ix_payments_user_id_status", "user_id", "status"),
        Index("ix_payments_listing_id", "listing_id"),
        Index("ix_payments_provider_reference", "provider_reference"),
        Index("ix_payments_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"


class PaymentTransaction(Base, UUIDMixin, TimestampMixin):
    """Payment transaction log model."""

    __tablename__ = "payment_transactions"

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    request_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    response_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    payment: Mapped["Payment"] = relationship(
        "Payment",
        back_populates="transactions",
    )

    __table_args__ = (
        Index("ix_payment_transactions_payment_id", "payment_id"),
        Index("ix_payment_transactions_provider_reference", "provider_reference"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<PaymentTransaction(id={self.id}, type={self.transaction_type}, status={self.status})>"


from src.models.user import User
from src.models.listing import Listing