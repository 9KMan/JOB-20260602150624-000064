"""Payments API router."""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentListResponse,
    PaymentInitRequest,
    PaymentInitResponse,
    RefundRequest,
    RefundResponse,
)
from src.services.payment_service import PaymentService
from src.middleware.auth import get_current_user
from src.models.user import User

router = APIRouter()


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    """Get payment service instance."""
    return PaymentService(db)


@router.post("/init", response_model=PaymentInitResponse)
async def initialize_payment(
    payment_data: PaymentInitRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PaymentInitResponse:
    """Initialize a payment with the selected provider."""
    result = await service.initialize_payment(payment_data, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to initialize payment",
        )
    return result


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    service: Annotated[PaymentService, Depends(get_payment_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = None,
    payment_method: str | None = None,
) -> dict:
    """List payments for the current user."""
    return await service.list_payments(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
        payment_method=payment_method,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get payment by ID."""
    payment = await service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment",
        )
    return payment


@router.post("/{payment_id}/capture", response_model=PaymentResponse)
async def capture_payment(
    payment_id: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Capture an authorized payment."""
    payment = await service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to capture this payment",
        )

    captured_payment = await service.capture_payment(payment_id)
    if not captured_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to capture payment",
        )
    return captured_payment


@router.post("/{payment_id}/cancel", response_model=PaymentResponse)
async def cancel_payment(
    payment_id: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Cancel a pending or authorized payment."""
    payment = await service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this payment",
        )

    cancelled_payment = await service.cancel_payment(payment_id)
    if not cancelled_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel payment",
        )
    return cancelled_payment


@router.post("/refund", response_model=RefundResponse)
async def refund_payment(
    refund_data: RefundRequest,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RefundResponse:
    """Process a refund for a completed payment."""
    result = await service.refund_payment(
        payment_id=refund_data.payment_id,
        amount=refund_data.amount,
        reason=refund_data.reason,
        user_id=current_user.id,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process refund",
        )
    return result


@router.get("/methods/available", response_model=dict)
async def get_available_payment_methods() -> dict:
    """Get list of available payment methods."""
    return {
        "payment_methods": [
            {
                "id": "ccbill",
                "name": "CCBill",
                "supported_types": ["visa", "mastercard", "amex", "discover"],
            },
            {
                "id": "paxum",
                "name": "Paxum",
                "supported_types": ["ewallet"],
            },
        ]
    }