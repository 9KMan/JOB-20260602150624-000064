"""Audit log Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""

    id: datetime
    user_id: datetime | None = None
    action: str
    resource_type: str
    resource_id: datetime | None = None
    old_values: dict | None = None
    new_values: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None
    endpoint: str | None = None
    method: str | None = None
    status_code: int | None = None
    error_message: str | None = None
    metadata: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list response."""

    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuditLogQuery(BaseModel):
    """Schema for audit log query parameters."""

    user_id: datetime | None = None
    action: str | None = None
    resource_type: str | None = None
    resource_id: datetime | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    page: int = 1
    page_size: int = 50