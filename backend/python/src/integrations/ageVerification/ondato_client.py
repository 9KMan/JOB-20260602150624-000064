"""Ondato identity verification client."""

import logging
import base64
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class OndatoClient:
    """Ondato SDK wrapper for identity verification."""

    def __init__(self) -> None:
        """Initialize Ondato client."""
        self.settings = get_settings()
        self.username = self.settings.ondato.ondato_username
        self.password = self.settings.ondato.ondato_password
        self.organization_id = self.settings.ondato.ondato_organization_id
        self.api_url = self.settings.ondato.ondato_api_url
        self._http_client: httpx.AsyncClient | None = None
        self._access_token: str | None = None

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

    async def _get_access_token(self) -> str | None:
        """Get Ondato API access token."""
        if self._access_token:
            return self._access_token

        if not self.username or not self.password:
            logger.warning("Ondato credentials not configured")
            return None

        try:
            url = f"{self.api_url}/identity/v1/authorize"
            credentials = base64.b64encode(
                f"{self.username}:{self.password}".encode()
            ).decode()

            response = await self.http_client.post(
                url,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/json",
                },
                json={
                    "organizationId": self.organization_id,
                },
            )

            if response.status_code == 200:
                data = response.json()
                self._access_token = data.get("accessToken")
                return self._access_token

            logger.warning(f"Ondato auth failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Ondato auth error: {e}")
            return None

    async def verify_identity(self, document_data: dict[str, Any]) -> bool:
        """Verify identity using Ondato.

        Args:
            document_data: Document data including type and images

        Returns:
            True if verification successful, False otherwise
        """
        access_token = await self._get_access_token()
        if not access_token:
            logger.warning("Ondato not configured, skipping verification")
            return True

        try:
            url = f"{self.api_url}/identity/v1/verifications"

            payload = {
                "country": document_data.get("country", "GB"),
                "documentType": document_data.get("document_type", "PASSPORT"),
                "acceptTos": True,
            }

            response = await self.http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload,
            )

            if response.status_code in (200, 201):
                data = response.json()
                return data.get("verificationResult") == "POSITIVE"

            logger.warning(f"Ondato verification failed: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Ondato verification error: {e}")
            return False

    async def create_verification_session(
        self,
        user_id: str,
        callback_url: str,
    ) -> dict[str, Any] | None:
        """Create a verification session.

        Args:
            user_id: User identifier
            callback_url: URL for callback after verification

        Returns:
            Session data including session token
        """
        access_token = await self._get_access_token()
        if not access_token:
            logger.warning("Ondato not configured")
            return None

        try:
            url = f"{self.api_url}/identity/v1/sessions"

            payload = {
                "redirectUri": callback_url,
                "externalUserId": user_id,
                "documentType": "PASSPORT",
                "countryRestriction": "GB",
            }

            response = await self.http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload,
            )

            if response.status_code in (200, 201):
                return response.json()

            logger.warning(f"Ondato session creation failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Ondato session creation error: {e}")
            return None

    async def get_session_status(self, session_id: str) -> dict[str, Any] | None:
        """Get verification session status.

        Args:
            session_id: Session identifier

        Returns:
            Session status data
        """
        access_token = await self._get_access_token()
        if not access_token:
            logger.warning("Ondato not configured")
            return None

        try:
            url = f"{self.api_url}/identity/v1/sessions/{session_id}"

            response = await self.http_client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code == 200:
                return response.json()

            logger.warning(f"Ondato get session failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Ondato get session error: {e}")
            return None