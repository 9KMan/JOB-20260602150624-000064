"""Base model mixins."""

import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from src.database import Base


class UUIDMixin:
    """Mixin for UUID primary key."""

    id: Mapped[Annotated[uuid.UUID, "primary key"]] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        sort_key=True,
    )


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)


class AuditMixin:
    """Mixin for audit trail."""

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )