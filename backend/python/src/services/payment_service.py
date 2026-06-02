"""Payment service with business logic."""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.models.payment import Payment, PaymentStatus, PaymentMethod, PaymentType, PaymentTransaction
from src.schemas.payment import PaymentInitRequest, PaymentInitResponse, RefundResponse
from src.integrations.payments.ccbill_client import CCBillClient
from src.integrations.payments.paxum_client import PaxumClient

logger = logging.getLogger(__name__)


class PaymentService:
    """Service class for payment operations."""

    def __init__(self, db: Session) -> None:
        """Initialize payment service."""
        self.db = db
        self.ccbill_client = CCBillClient()
        self.paxum_client = PaxumClient()

    async def get_payment_by_id(self, payment_id: str) -> Payment | None:
        """Get payment by ID."""
        try:
            payment_uuid = uuid.UUID(payment_id)
        except ValueError:
            return None

        return self.db.query(Payment).filter(Payment.id == payment_uuid).first()

    async def get_payment_by_provider_reference(self, provider_ref: str) -> Payment | None:
        """Get payment by provider reference."""
        return self.db.query(Payment).filter(Payment.provider_reference == provider_ref).first()

    async def initialize_payment(
        self,
        payment_data: PaymentInitRequest,
        user_id: uuid.UUID,
    ) -> PaymentInitResponse | None:
        """Initialize a payment with the selected provider."""
        payment = Payment(
            user_id=user_id,
            listing_id=uuid.UUID(str(payment_data.listing_id)) if payment_data.listing_id else None,
            status=PaymentStatus.PENDING,
            payment_method=PaymentMethod(payment_data.payment_method),
            payment_type=PaymentType(payment_data.payment_type),
            amount=payment_data.amount,
            currency=payment_data.currency,
            description=f"{payment_data.payment_type} payment",
            is_test=payment_data.is_test,
        )

        self.db.add(payment)
        self.db.flush()

        try:
            if payment_data.payment_method == "ccbill":
                result = await self.ccbill_client.initialize_payment(
                    amount=float(payment_data.amount),
                    currency=payment_data.currency,
                    payment_id=str(payment.id),
                    return_url=payment_data.return_url,
                )
                payment.provider_reference = result.get("provider_reference")
                self.db.commit()
                return PaymentInitResponse(
                    payment_id=str(payment.id),
                    redirect_url=result.get("redirect_url"),
                    form_data=result.get("form_data"),
                    provider_reference=result.get("provider_reference"),
                )

            elif payment_data.payment_method == "paxum":
                result = await self.paxum_client.initialize_payment(
                    amount=float(payment_data.amount),
                    currency=payment_data.currency,
                    payment_id=str(payment.id),
                    return_url=payment_data.return_url,
                )
                payment.provider_reference = result.get("provider_reference")
                self.db.commit()
                return PaymentInitResponse(
                    payment_id=str(payment.id),
                    redirect_url=result.get("redirect_url"),
                    provider_reference=result.get("provider_reference"),
                )

        except Exception as e:
            logger.error(f"Failed to initialize payment: {e}")
            payment.status = PaymentStatus.FAILED
            self.db.commit()
            return None

        return None

    async def list_payments(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        payment_method: str | None = None,
    ) -> dict:
        """List payments for a user."""
        query = self.db.query(Payment).filter(Payment.user_id == user_id)

        if status:
            try:
                status_enum = PaymentStatus(status)
                query = query.filter(Payment.status == status_enum)
            except ValueError:
                pass

        if payment_method:
            try:
                method_enum = PaymentMethod(payment_method)
                query = query.filter(Payment.payment_method == method_enum)
            except ValueError:
                pass

        total = query.count()

        payments = query.order_by(Payment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        total_pages = (total + page_size - 1) // page_size

        return {
            "items": payments,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def capture_payment(self, payment_id: str) -> Payment | None:
        """Capture an authorized payment."""
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            return None

        if payment.status != PaymentStatus.AUTHORIZED:
            return None

        try:
            if payment.payment_method == PaymentMethod.CCBILL:
                success = await self.ccbill_client.capture_payment(payment.provider_reference)
            elif payment.payment_method == PaymentMethod.PAXUM:
                success = await self.paxum_client.capture_payment(payment.provider_reference)
            else:
                return None

            if success:
                payment.status = PaymentStatus.CAPTURED
                payment.completed_at = datetime.now(timezone.utc)
                self._add_transaction(payment, "capture", "completed")
                self.db.commit()
                self.db.refresh(payment)

        except Exception as e:
            logger.error(f"Failed to capture payment {payment_id}: {e}")
            self._add_transaction(payment, "capture", "failed", error_message=str(e))
            self.db.commit()
            return None

        return payment

    async def cancel_payment(self, payment_id: str) -> Payment | None:
        """Cancel a pending or authorized payment."""
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            return None

        if payment.status not in [PaymentStatus.PENDING, PaymentStatus.AUTHORIZED]:
            return None

        try:
            payment.status = PaymentStatus.VOIDED
            self._add_transaction(payment, "cancel", "completed")
            self.db.commit()
            self.db.refresh(payment)
        except Exception as e:
            logger.error(f"Failed to cancel payment {payment_id}: {e}")
            return None

        return payment

    async def refund_payment(
        self,
        payment_id: str,
        amount: Decimal | None,
        reason: str | None,
        user_id: uuid.UUID,
    ) -> RefundResponse | None:
        """Process a refund for a completed payment."""
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            return None

        if payment.user_id != user_id:
            return None

        if payment.status != PaymentStatus.COMPLETED:
            return None

        refund_amount = amount if amount else payment.amount

        if refund_amount > (payment.amount - payment.refunded_amount):
            return None

        try:
            if payment.payment_method == PaymentMethod.CCBILL:
                success = await self.ccbill_client.refund_payment(
                    payment.provider_reference,
                    float(refund_amount),
                )
            elif payment.payment_method == PaymentMethod.PAXUM:
                success = await self.paxum_client.refund_payment(
                    payment.provider_reference,
                    float(refund_amount),
                )
            else:
                return None

            if success:
                payment.refunded_amount += refund_amount

                if payment.refunded_amount >= payment.amount:
                    payment.status = PaymentStatus.REFUNDED
                else:
                    payment.status = PaymentStatus.PARTIALLY_REFUNDED

                self._add_transaction(
                    payment,
                    "refund",
                    "completed",
                    amount=float(refund_amount),
                )
                self.db.commit()
                self.db.refresh(payment)

                return RefundResponse(
                    payment_id=str(payment.id),
                    refunded_amount=refund_amount,
                    status=payment.status.value,
                    refund_reference=f"ref_{uuid.uuid4().hex[:12]}",
                )

        except Exception as e:
            logger.error(f"Failed to refund payment {payment_id}: {e}")
            self._add_transaction(payment, "refund", "failed", error_message=str(e))
            self.db.commit()
            return None

        return None

    async def handle_ccbill_sale(self, payment_id: str, data: dict) -> None:
        """Handle CCBill sale notification."""
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            logger.warning(f"CCBill sale for unknown payment: {payment_id}")
            return

        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.now(timezone.utc)
        payment.provider_response = data
        self._add_transaction(payment, "sale", "completed", response_data=data)
        self.db.commit()

        logger.info(f"CCBill sale processed for payment: {payment_id}")

    async def handle_ccbill_refund(self, transaction_id: str, data: dict) -> None:
        """Handle CCBill refund notification."""
        payment = await self.get_payment_by_provider_reference(transaction_id)
        if not payment:
            logger.warning(f"CCBill refund for unknown transaction: {transaction_id}")
            return

        refund_amount = Decimal(str(data.get("refundAmount", 0)))
        payment.refunded_amount += refund_amount

        if payment.refunded_amount >= payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED

        self._add_transaction(payment, "refund", "completed", response_data=data)
        self.db.commit()

        logger.info(f"CCBill refund processed for payment: {payment.id}")

    async def handle_ccbill_void(self, transaction_id: str, data: dict) -> None:
        """Handle CCBill void notification."""
        payment = await self.get_payment_by_provider_reference(transaction_id)
        if not payment:
            logger.warning(f"CCBill void for unknown transaction: {transaction_id}")
            return

        payment.status = PaymentStatus.VOIDED
        self._add_transaction(payment, "void", "completed", response_data=data)
        self.db.commit()

        logger.info(f"CCBill void processed for payment: {payment.id}")

    async def handle_paxum_payment(self, payment_id: str, data: dict) -> None:
        """Handle Paxum payment notification."""
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            logger.warning(f"Paxum payment for unknown payment: {payment_id}")
            return

        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.now(timezone.utc)
        payment.provider_response = data
        self._add_transaction(payment, "payment", "completed", response_data=data)
        self.db.commit()

        logger.info(f"Paxum payment processed for payment: {payment_id}")

    async def handle_paxum_refund(self, reference: str, data: dict) -> None:
        """Handle Paxum refund notification."""
        payment = await self.get_payment_by_provider_reference(reference)
        if not payment:
            logger.warning(f"Paxum refund for unknown reference: {reference}")
            return

        refund_amount = Decimal(str(data.get("refund_amount", 0)))
        payment.refunded_amount += refund_amount

        if payment.refunded_amount >= payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED

        self._add_transaction(payment, "refund", "completed", response_data=data)
        self.db.commit()

        logger.info(f"Paxum refund processed for payment: {payment.id}")

    def _add_transaction(
        self,
        payment: Payment,
        transaction_type: str,
        status: str,
        amount: float | None = None,
        request_data: dict | None = None,
        response_data: dict | None = None,
        error_message: str | None = None,
    ) -> PaymentTransaction:
        """Add a payment transaction log entry."""
        transaction = PaymentTransaction(
            payment_id=payment.id,
            transaction_type=transaction_type,
            amount=amount if amount else float(payment.amount),
            currency=payment.currency,
            status=status,
            provider_reference=payment.provider_reference,
            request_data=request_data,
            response_data=response_data,
            error_message=error_message,
        )

        self.db.add(transaction)
        return transaction