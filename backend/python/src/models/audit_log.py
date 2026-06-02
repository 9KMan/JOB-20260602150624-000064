"""Audit log model."""

import enum
import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import String, Text, DateTime, Enum, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.models.base import UUIDMixin, TimestampMixin


class AuditAction(enum.Enum):
    """Audit log action types."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SOFT_DELETE = "soft_delete"
    RESTORE = "restore"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    EMAIL_VERIFIED = "email_verified"
    PHONE_VERIFIED = "phone_verified"
    AGE_VERIFIED = "age_verified"
    LISTING_PUBLISHED = "listing_published"
    LISTING_SUSPENDED = "listing_suspended"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_REFUNDED = "payment_refunded"


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """Audit log model for tracking changes and actions."""

    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction),
        nullable=False,
    )
    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    old_values: Mapped[dict | None] = mapped_column(
        nullable=True,
    )
    new_values: Mapped[dict | None] = mapped_column(
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
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    endpoint: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    method: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )
    status_code: Mapped[int | None] = mapped_column(
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    metadata: Mapped[dict | None] = mapped_column(
        nullable=True,
    )

    __table_args__ = (
        Index("ix_audit_logs_user_id_created", "user_id", "created_at"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_action_created", "action", "created_at"),
        Index("ix_audit_logs_request_id", "request_id"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type})>"