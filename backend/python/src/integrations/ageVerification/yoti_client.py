"""Yoti age verification client wrapper."""

import logging
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class YotiClient:
    """Yoti SDK wrapper for age verification."""

    def __init__(self) -> None:
        """Initialize Yoti client."""
        self.settings = get_settings()
        self.client_sdk_id = self.settings.yoti.yoti_client_sdk_id
        self.pem_file = self.settings.yoti.yoti_pem_file
        self.api_url = "https://api.yoti.com"
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

    async def verify_age(self, verification_token: str) -> bool:
        """Verify age using Yoti token.

        Args:
            verification_token: Token from Yoti SDK

        Returns:
            True if verification successful, False otherwise
        """
        if not self.client_sdk_id or not self.pem_file:
            logger.warning("Yoti not configured, skipping verification")
            return True

        try:
            url = f"{self.api_url}/api/v1/age-verification/token/verify"
            payload = {
                "token": verification_token,
                "client_sdk_id": self.client_sdk_id,
            }

            response = await self.http_client.post(
                url,
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("result", {}).get("age_verified", False)

            logger.warning(f"Yoti verification failed: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Yoti verification error: {e}")
            return False

    async def create_session(self, user_id: str, callback_url: str) -> dict[str, Any] | None:
        """Create a Yoti session for document verification.

        Args:
            user_id: User identifier
            callback_url: URL for callback after verification

        Returns:
            Session data including session ID and SDK token
        """
        if not self.client_sdk_id or not self.pem_file:
            logger.warning("Yoti not configured")
            return None

        try:
            url = f"{self.api_url}/api/v1/sessions"
            payload = {
                "client_sdk_id": self.client_sdk_id,
                "callback_url": callback_url,
                "subject_id": user_id,
                "age_verification": {
                    "requested": True,
                    "accepted_types": ["PASSPORT", "DRIVING_LICENSE", "NATIONAL_ID"],
                },
            }

            response = await self.http_client.post(
                url,
                json=payload,
            )

            if response.status_code in (200, 201):
                return response.json()

            logger.warning(f"Yoti session creation failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Yoti session creation error: {e}")
            return None

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get Yoti session status.

        Args:
            session_id: Session identifier

        Returns:
            Session data
        """
        if not self.client_sdk_id or not self.pem_file:
            logger.warning("Yoti not configured")
            return None

        try:
            url = f"{self.api_url}/api/v1/sessions/{session_id}"

            response = await self.http_client.get(url)

            if response.status_code == 200:
                return response.json()

            logger.warning(f"Yoti get session failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Yoti get session error: {e}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete a Yoti session.

        Args:
            session_id: Session identifier

        Returns:
            True if deletion successful
        """
        if not self.client_sdk_id or not self.pem_file:
            logger.warning("Yoti not configured")
            return False

        try:
            url = f"{self.api_url}/api/v1/sessions/{session_id}"

            response = await self.http_client.delete(url)

            return response.status_code == 204

        except Exception as e:
            logger.error(f"Yoti delete session error: {e}")
            return False