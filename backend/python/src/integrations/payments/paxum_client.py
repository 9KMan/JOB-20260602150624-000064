"""Paxum payment processor client."""

import hashlib
import hmac
import logging
import time
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class PaxumClient:
    """Paxum payment processor API client."""

    def __init__(self) -> None:
        """Initialize Paxum client."""
        self.settings = get_settings()
        self.api_key = self.settings.paxum.paxum_api_key
        self.api_url = self.settings.paxum.paxum_api_url
        self._http_client: httpx.AsyncClient | None = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                headers={"X-API-KEY": self.api_key} if self.api_key else {},
            )
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def initialize_payment(
        self,
        amount: float,
        currency: str,
        payment_id: str,
        return_url: str | None = None,
    ) -> dict[str, Any]:
        """Initialize a Paxum payment.

        Args:
            amount: Payment amount
            currency: Currency code
            payment_id: Internal payment ID
            return_url: Return URL after payment

        Returns:
            Payment initialization data including redirect URL
        """
        if not self.api_key:
            logger.warning("Paxum not configured")
            return {
                "redirect_url": return_url or "",
                "provider_reference": f"paxum_{payment_id}",
            }

        try:
            url = f"{self.api_url}/v1/checkout"

            payload = {
                "amount": f"{amount:.2f}",
                "currency": currency,
                "order_id": payment_id,
                "return_url": return_url,
                "cancel_url": return_url,
                "callback_url": f"{self.api_url}/webhook",
            }

            response = await self.http_client.post(url, json=payload)

            if response.status_code in (200, 201):
                data = response.json()
                return {
                    "redirect_url": data.get("checkout_url", return_url or ""),
                    "provider_reference": data.get("transaction_id", f"paxum_{payment_id}"),
                }

            logger.warning(f"Paxum initialization failed: {response.status_code}")
            return {
                "redirect_url": return_url or "",
                "provider_reference": f"paxum_{payment_id}",
            }

        except Exception as e:
            logger.error(f"Paxum payment initialization error: {e}")
            return {
                "redirect_url": "",
                "provider_reference": None,
            }

    async def capture_payment(self, provider_reference: str) -> bool:
        """Capture an authorized Paxum payment.

        Args:
            provider_reference: Provider reference ID

        Returns:
            True if capture successful
        """
        if not provider_reference or not self.api_key:
            return False

        try:
            url = f"{self.api_url}/v1/transactions/{provider_reference}/capture"

            response = await self.http_client.post(url)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Paxum capture error: {e}")
            return False

    async def refund_payment(
        self,
        provider_reference: str,
        amount: float,
    ) -> bool:
        """Refund a Paxum payment.

        Args:
            provider_reference: Provider reference ID
            amount: Refund amount

        Returns:
            True if refund successful
        """
        if not provider_reference or not self.api_key:
            return False

        try:
            url = f"{self.api_url}/v1/transactions/{provider_reference}/refund"

            payload = {
                "amount": f"{amount:.2f}",
            }

            response = await self.http_client.post(url, json=payload)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Paxum refund error: {e}")
            return False

    async def get_transaction_status(self, provider_reference: str) -> dict[str, Any] | None:
        """Get Paxum transaction status.

        Args:
            provider_reference: Provider reference ID

        Returns:
            Transaction status data
        """
        if not provider_reference or not self.api_key:
            return None

        try:
            url = f"{self.api_url}/v1/transactions/{provider_reference}"

            response = await self.http_client.get(url)

            if response.status_code == 200:
                return response.json()

            return None

        except Exception as e:
            logger.error(f"Paxum get status error: {e}")
            return None