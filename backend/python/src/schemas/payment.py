"""Payment Pydantic schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    """Base payment schema."""

    payment_method: str
    payment_type: str
    amount: Decimal = Field(ge=0)
    currency: str = Field(default="USD", max_length=3)
    description: str | None = None
    metadata: dict | None = None


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""

    listing_id: datetime | None = None
    is_test: bool = False


class PaymentResponse(BaseModel):
    """Schema for payment response."""

    id: datetime
    user_id: datetime | None = None
    listing_id: datetime | None = None
    status: str
    payment_method: str
    payment_type: str
    amount: Decimal
    currency: str
    provider_reference: str | None = None
    description: str | None = None
    metadata: dict | None = None
    completed_at: datetime | None = None
    refunded_amount: Decimal
    is_test: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentListResponse(BaseModel):
    """Schema for paginated payment list response."""

    items: list[PaymentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaymentWebhook(BaseModel):
    """Schema for payment webhook payload."""

    event_type: str
    payment_id: str
    provider_reference: str | None = None
    status: str
    amount: Decimal | None = None
    currency: str | None = None
    timestamp: datetime
    signature: str | None = None
    data: dict | None = None


class PaymentInitRequest(BaseModel):
    """Schema for payment initialization request."""

    payment_method: str = Field(pattern=r"^(ccbill|paxum)$")
    payment_type: str = Field(pattern=r"^(subscription|listing_promotion|verification|other)$")
    amount: Decimal = Field(ge=0, decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    listing_id: datetime | None = None
    user_id: datetime | None = None
    return_url: str | None = None
    webhook_url: str | None = None


class PaymentInitResponse(BaseModel):
    """Schema for payment initialization response."""

    payment_id: str
    redirect_url: str | None = None
    form_data: dict | None = None
    provider_reference: str | None = None


class RefundRequest(BaseModel):
    """Schema for refund request."""

    payment_id: str
    amount: Decimal | None = Field(default=None, ge=0)
    reason: str | None = None


class RefundResponse(BaseModel):
    """Schema for refund response."""

    payment_id: str
    refunded_amount: Decimal
    status: str
    refund_reference: str | None = None