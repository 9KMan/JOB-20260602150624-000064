"""Mautic marketing automation client."""

import logging
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class MauticClient:
    """Mautic marketing automation API client."""

    def __init__(self) -> None:
        """Initialize Mautic client."""
        self.settings = get_settings()
        self.url = self.settings.mautic.mautic_url
        self.username = self.settings.mautic.mautic_username
        self.password = self.settings.mautic.mautic_password
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
        """Get Mautic API access token."""
        if self._access_token:
            return self._access_token

        if not self.url or not self.username or not self.password:
            logger.warning("Mautic not configured")
            return None

        try:
            url = f"{self.url}/oauth/v2/token"
            payload = {
                "grant_type": "password",
                "client_id": self.username,
                "client_secret": self.password,
                "username": self.username,
                "password": self.password,
            }

            response = await self.http_client.post(url, data=payload)

            if response.status_code == 200:
                data = response.json()
                self._access_token = data.get("access_token")
                return self._access_token

            logger.warning(f"Mautic auth failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Mautic auth error: {e}")
            return None

    async def create_contact(self, contact_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new contact in Mautic.

        Args:
            contact_data: Contact data including email, firstname, lastname

        Returns:
            Created contact data
        """
        access_token = await self._get_access_token()
        if not access_token:
            return None

        try:
            url = f"{self.url}/api/contacts/new"

            payload = {
                "email": contact_data.get("email"),
                "firstname": contact_data.get("first_name"),
                "lastname": contact_data.get("last_name"),
                "phone": contact_data.get("phone"),
            }

            response = await self.http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload,
            )

            if response.status_code in (200, 201):
                data = response.json()
                return data.get("contact")

            logger.warning(f"Mautic create contact failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Mautic create contact error: {e}")
            return None

    async def update_contact(
        self,
        contact_id: int,
        contact_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update a contact in Mautic.

        Args:
            contact_id: Contact ID
            contact_data: Updated contact data

        Returns:
            Updated contact data
        """
        access_token = await self._get_access_token()
        if not access_token:
            return None

        try:
            url = f"{self.url}/api/contacts/{contact_id}/edit"

            payload = {
                "email": contact_data.get("email"),
                "firstname": contact_data.get("first_name"),
                "lastname": contact_data.get("last_name"),
                "phone": contact_data.get("phone"),
            }

            response = await self.http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("contact")

            logger.warning(f"Mautic update contact failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Mautic update contact error: {e}")
            return None

    async def get_contact(self, contact_id: int) -> dict[str, Any] | None:
        """Get a contact by ID.

        Args:
            contact_id: Contact ID

        Returns:
            Contact data
        """
        access_token = await self._get_access_token()
        if not access_token:
            return None

        try:
            url = f"{self.url}/api/contacts/{contact_id}"

            response = await self.http_client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("contact")

            logger.warning(f"Mautic get contact failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Mautic get contact error: {e}")
            return None

    async def get_contact_by_email(self, email: str) -> dict[str, Any] | None:
        """Get a contact by email.

        Args:
            email: Email address

        Returns:
            Contact data
        """
        access_token = await self._get_access_token()
        if not access_token:
            return None

        try:
            url = f"{self.url}/api/contacts"
            params = {"search": email}

            response = await self.http_client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
            )

            if response.status_code == 200:
                data = response.json()
                contacts = data.get("contacts", {})
                if contacts:
                    return list(contacts.values())[0].get("profile")

            logger.warning(f"Mautic get contact by email failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Mautic get contact by email error: {e}")
            return None

    async def add_to_segment(
        self,
        contact_id: int,
        segment_id: int,
    ) -> bool:
        """Add a contact to a segment.

        Args:
            contact_id: Contact ID
            segment_id: Segment ID

        Returns:
            True if successful
        """
        access_token = await self._get_access_token()
        if not access_token:
            return False

        try:
            url = f"{self.url}/api/segments/{segment_id}/contact/{contact_id}/add"

            response = await self.http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Mautic add to segment error: {e}")
            return False

    async def remove_from_segment(
        self,
        contact_id: int,
        segment_id: int,
    ) -> bool:
        """Remove a contact from a segment.

        Args:
            contact_id: Contact ID
            segment_id: Segment ID

        Returns:
            True if successful
        """
        access_token = await self._get_access_token()
        if not access_token:
            return False

        try:
            url = f"{self.url}/api/segments/{segment_id}/contact/{contact_id}/remove"

            response = await self.http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Mautic remove from segment error: {e}")
            return False

    async def create_campaign_event(
        self,
        campaign_id: int,
        event_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Create a campaign event.

        Args:
            campaign_id: Campaign ID
            event_data: Event data

        Returns:
            Created event data
        """
        access_token = await self._get_access_token()
        if not access_token:
            return None

        try:
            url = f"{self.url}/api/campaigns/{campaign_id}/events"

            response = await self.http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=event_data,
            )

            if response.status_code in (200, 201):
                return response.json()

            logger.warning(f"Mautic create campaign event failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Mautic create campaign event error: {e}")
            return None