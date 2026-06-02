"""CCBill payment processor client."""

import hashlib
import hmac
import logging
import time
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class CCBillClient:
    """CCBill payment processor API client."""

    def __init__(self) -> None:
        """Initialize CCBill client."""
        self.settings = get_settings()
        self.account_number = self.settings.ccbill.ccbill_account_number
        self.sub_account_number = self.settings.ccbill.ccbill_sub_account_number
        self.salt = self.settings.ccbill.ccbill_salt
        self.flexid = self.settings.ccbill.ccbill_flexid
        self.salt_key = self.settings.ccbill.ccbill_salt_key
        self.dataform_salt = self.settings.ccbill.ccbill_dataform_salt
        self.api_url = self.settings.ccbill.ccbill_api_url
        self._http_client: httpx.AsyncClient | None = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def _generate_digest(self, data: str) -> str:
        """Generate CCBill digest for verification.

        Args:
            data: Data string to hash

        Returns:
            MD5 hash digest
        """
        return hashlib.md5(data.encode()).hexdigest()

    def _generate_form_digest(self, params: dict[str, Any]) -> str:
        """Generate form digest for CCBill.

        Args:
            params: Form parameters

        Returns:
            Form digest
        """
        order_types = {
            "subscription": "ccbill",
            "recurring": "ccbill_recurring",
            "lifetime": "ccbill_lifetime",
            "single": "ccbill_single",
        }

        base = (
            f"{params.get('clientAccnum', '')}"
            f"{params.get('clientSubacc', '')}"
            f"{params.get('initialPrice', '')}"
            f"{params.get('initialPeriod', '')}"
            f"{params.get('recurringPrice', '')}"
            f"{params.get('recurringPeriod', '')}"
            f"{params.get('numRecurrences', '')}"
            f"{self.dataform_salt}"
        )

        return self._generate_digest(base)

    async def initialize_payment(
        self,
        amount: float,
        currency: str,
        payment_id: str,
        return_url: str | None = None,
    ) -> dict[str, Any]:
        """Initialize a CCBill payment.

        Args:
            amount: Payment amount
            currency: Currency code
            payment_id: Internal payment ID
            return_url: Return URL after payment

        Returns:
            Payment initialization data including redirect URL
        """
        if not self.account_number or not self.sub_account_number:
            logger.warning("CCBill not configured")
            return {
                "redirect_url": return_url or "",
                "form_data": {},
                "provider_reference": f"ccbill_{payment_id}",
            }

        try:
            params = {
                "clientAccnum": self.account_number,
                "clientSubacc": self.sub_account_number,
                "initialPrice": f"{amount:.2f}",
                "initialPeriod": "30",
                "recurringPrice": f"{amount:.2f}",
                "recurringPeriod": "30",
                "numRecurrences": "99",
                "currency": currency,
                "orderid": payment_id,
                "returnUrl": return_url,
                "returnUrlCancel": return_url,
                "returnUrlDeclined": return_url,
            }

            params["formDigest"] = self._generate_form_digest(params)

            form_data = {
                "url": f"{self.api_url}/datalink2ccbill.ccbill",
                "params": params,
            }

            redirect_url = f"{self.api_url}/checkout/{self.flexid}"

            return {
                "redirect_url": redirect_url,
                "form_data": form_data,
                "provider_reference": f"ccbill_{payment_id}",
            }

        except Exception as e:
            logger.error(f"CCBill payment initialization error: {e}")
            return {
                "redirect_url": "",
                "form_data": {},
                "provider_reference": None,
            }

    async def capture_payment(self, provider_reference: str) -> bool:
        """Capture an authorized CCBill payment.

        Args:
            provider_reference: Provider reference ID

        Returns:
            True if capture successful
        """
        if not provider_reference or not self.salt:
            return False

        try:
            url = f"{self.api_url}/api/sale"

            timestamp = int(time.time())
            data = f"{provider_reference}{timestamp}{self.salt}"
            verification = hashlib.sha256(data.encode()).hexdigest()

            payload = {
                "transactionId": provider_reference,
                "timestamp": timestamp,
                "verification": verification,
            }

            response = await self.http_client.post(url, json=payload)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"CCBill capture error: {e}")
            return False

    async def refund_payment(
        self,
        provider_reference: str,
        amount: float,
    ) -> bool:
        """Refund a CCBill payment.

        Args:
            provider_reference: Provider reference ID
            amount: Refund amount

        Returns:
            True if refund successful
        """
        if not provider_reference or not self.salt:
            return False

        try:
            url = f"{self.api_url}/api/refund"

            timestamp = int(time.time())
            data = f"{provider_reference}{amount}{timestamp}{self.salt}"
            verification = hashlib.sha256(data.encode()).hexdigest()

            payload = {
                "transactionId": provider_reference,
                "amount": f"{amount:.2f}",
                "timestamp": timestamp,
                "verification": verification,
            }

            response = await self.http_client.post(url, json=payload)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"CCBill refund error: {e}")
            return False

    async def void_transaction(self, provider_reference: str) -> bool:
        """Void a CCBill transaction.

        Args:
            provider_reference: Provider reference ID

        Returns:
            True if void successful
        """
        if not provider_reference or not self.salt:
            return False

        try:
            url = f"{self.api_url}/api/void"

            timestamp = int(time.time())
            data = f"{provider_reference}{timestamp}{self.salt}"
            verification = hashlib.sha256(data.encode()).hexdigest()

            payload = {
                "transactionId": provider_reference,
                "timestamp": timestamp,
                "verification": verification,
            }

            response = await self.http_client.post(url, json=payload)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"CCBill void error: {e}")
            return False