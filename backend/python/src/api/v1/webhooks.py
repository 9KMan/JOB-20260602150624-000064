"""Webhooks API router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.payment import PaymentWebhook
from src.services.payment_service import PaymentService
from src.integrations.payments.webhook_handler import WebhookHandler

router = APIRouter()


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    """Get payment service instance."""
    return PaymentService(db)


def get_webhook_handler() -> WebhookHandler:
    """Get webhook handler instance."""
    return WebhookHandler()


@router.post("/ccbill")
async def ccbill_webhook(
    request: Request,
    handler: Annotated[WebhookHandler, Depends(get_webhook_handler)],
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> dict:
    """Handle CCBill webhook notifications."""
    try:
        body = await request.json()
        signature = request.headers.get("X-CCBill-Signature", "")

        is_valid = handler.verify_ccbill_signature(body, signature)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

        event_type = body.get("eventType")
        transaction_id = body.get("transactionId")
        payment_id = body.get("paymentId")

        if event_type == "NewSale" and payment_id:
            await service.handle_ccbill_sale(payment_id, body)
        elif event_type == "Refund" and transaction_id:
            await service.handle_ccbill_refund(transaction_id, body)
        elif event_type == "Void" and transaction_id:
            await service.handle_ccbill_void(transaction_id, body)

        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook processing failed: {str(e)}",
        )


@router.post("/paxum")
async def paxum_webhook(
    request: Request,
    handler: Annotated[WebhookHandler, Depends(get_webhook_handler)],
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> dict:
    """Handle Paxum webhook notifications."""
    try:
        body = await request.json()
        signature = request.headers.get("X-Paxum-Signature", "")

        is_valid = handler.verify_paxum_signature(body, signature)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

        event_type = body.get("event")
        payment_id = body.get("payment_id")
        reference = body.get("reference")

        if event_type == "payment_completed" and payment_id:
            await service.handle_paxum_payment(payment_id, body)
        elif event_type == "payment_refunded" and reference:
            await service.handle_paxum_refund(reference, body)

        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook processing failed: {str(e)}",
        )


@router.post("/yoti")
async def yoti_webhook(
    request: Request,
    handler: Annotated[WebhookHandler, Depends(get_webhook_handler)],
) -> dict:
    """Handle Yoti webhook notifications."""
    try:
        body = await request.json()
        signature = request.headers.get("X-Yoti-Signature", "")

        is_valid = handler.verify_yoti_signature(body, signature)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook processing failed: {str(e)}",
        )


@router.post("/ondato")
async def ondato_webhook(
    request: Request,
    handler: Annotated[WebhookHandler, Depends(get_webhook_handler)],
) -> dict:
    """Handle Ondato webhook notifications."""
    try:
        body = await request.json()
        signature = request.headers.get("X-Ondato-Signature", "")

        is_valid = handler.verify_ondato_signature(body, signature)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook processing failed: {str(e)}",
        )


@router.get("/providers")
async def get_webhook_endpoints() -> dict:
    """Get webhook endpoint URLs for external providers."""
    return {
        "endpoints": {
            "ccbill": "/api/v1/webhooks/ccbill",
            "paxum": "/api/v1/webhooks/paxum",
            "yoti": "/api/v1/webhooks/yoti",
            "ondato": "/api/v1/webhooks/ondato",
        }
    }