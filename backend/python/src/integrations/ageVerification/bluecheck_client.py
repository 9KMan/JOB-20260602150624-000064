"""BlueCheck age verification client."""

import logging
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class BlueCheckClient:
    """BlueCheck SDK wrapper for age verification."""

    def __init__(self) -> None:
        """Initialize BlueCheck client."""
        self.settings = get_settings()
        self.api_key = self.settings.bluecheck.bluecheck_api_key
        self.api_url = self.settings.bluecheck.bluecheck_api_url
        self._http_client: httpx.AsyncClient | None = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                headers={"X-API-Key": self.api_key} if self.api_key else {},
            )
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def verify_age(self, document_data: dict[str, Any]) -> bool:
        """Verify age using BlueCheck document verification.

        Args:
            document_data: Document data including type and number

        Returns:
            True if verification successful, False otherwise
        """
        if not self.api_key:
            logger.warning("BlueCheck not configured, skipping verification")
            return True

        try:
            url = f"{self.api_url}/v1/verify"
            payload = {
                "document_type": document_data.get("type"),
                "document_number": document_data.get("number"),
                "date_of_birth": document_data.get("date_of_birth"),
                "country": document_data.get("country", "AU"),
            }

            response = await self.http_client.post(
                url,
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("verified", False) or data.get("passed", False)

            logger.warning(f"BlueCheck verification failed: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"BlueCheck verification error: {e}")
            return False

    async def check_status(self, verification_id: str) -> dict[str, Any] | None:
        """Check verification status.

        Args:
            verification_id: Verification identifier

        Returns:
            Status data
        """
        if not self.api_key:
            logger.warning("BlueCheck not configured")
            return None

        try:
            url = f"{self.api_url}/v1/verify/{verification_id}"

            response = await self.http_client.get(url)

            if response.status_code == 200:
                return response.json()

            logger.warning(f"BlueCheck status check failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"BlueCheck status check error: {e}")
            return None

    async def create_check(self, customer_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new age verification check.

        Args:
            customer_data: Customer data including name, DOB, document info

        Returns:
            Check data including verification URL
        """
        if not self.api_key:
            logger.warning("BlueCheck not configured")
            return None

        try:
            url = f"{self.api_url}/v1/check"
            payload = {
                "customer": {
                    "first_name": customer_data.get("first_name"),
                    "last_name": customer_data.get("last_name"),
                    "date_of_birth": customer_data.get("date_of_birth"),
                    "email": customer_data.get("email"),
                },
                "document": {
                    "type": customer_data.get("document_type"),
                    "country": customer_data.get("document_country", "AU"),
                },
            }

            response = await self.http_client.post(
                url,
                json=payload,
            )

            if response.status_code in (200, 201):
                return response.json()

            logger.warning(f"BlueCheck create check failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"BlueCheck create check error: {e}")
            return None