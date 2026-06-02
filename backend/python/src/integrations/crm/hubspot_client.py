"""HubSpot CRM client."""

import logging
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class HubSpotClient:
    """HubSpot CRM API client."""

    def __init__(self) -> None:
        """Initialize HubSpot client."""
        self.settings = get_settings()
        self.api_key = self.settings.hubspot.hubspot_api_key
        self.api_url = self.settings.hubspot.hubspot_api_url
        self._http_client: httpx.AsyncClient | None = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            )
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def create_contact(self, contact_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new contact in HubSpot.

        Args:
            contact_data: Contact data including email, firstname, lastname

        Returns:
            Created contact data
        """
        if not self.api_key:
            logger.warning("HubSpot not configured")
            return None

        try:
            url = f"{self.api_url}/crm/v3/objects/contacts"

            properties = {
                "email": contact_data.get("email"),
                "firstname": contact_data.get("first_name"),
                "lastname": contact_data.get("last_name"),
                "phone": contact_data.get("phone"),
            }

            response = await self.http_client.post(
                url,
                json={"properties": properties},
            )

            if response.status_code in (200, 201):
                return response.json()

            logger.warning(f"HubSpot create contact failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"HubSpot create contact error: {e}")
            return None

    async def update_contact(
        self,
        contact_id: str,
        contact_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update a contact in HubSpot.

        Args:
            contact_id: Contact ID
            contact_data: Updated contact data

        Returns:
            Updated contact data
        """
        if not self.api_key:
            logger.warning("HubSpot not configured")
            return None

        try:
            url = f"{self.api_url}/crm/v3/objects/contacts/{contact_id}"

            properties = {}
            if "email" in contact_data:
                properties["email"] = contact_data["email"]
            if "first_name" in contact_data:
                properties["firstname"] = contact_data["first_name"]
            if "last_name" in contact_data:
                properties["lastname"] = contact_data["last_name"]
            if "phone" in contact_data:
                properties["phone"] = contact_data["phone"]

            response = await self.http_client.patch(
                url,
                json={"properties": properties},
            )

            if response.status_code == 200:
                return response.json()

            logger.warning(f"HubSpot update contact failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"HubSpot update contact error: {e}")
            return None

    async def get_contact(self, contact_id: str) -> dict[str, Any] | None:
        """Get a contact by ID.

        Args:
            contact_id: Contact ID

        Returns:
            Contact data
        """
        if not self.api_key:
            logger.warning("HubSpot not configured")
            return None

        try:
            url = f"{self.api_url}/crm/v3/objects/contacts/{contact_id}"

            response = await self.http_client.get(url)

            if response.status_code == 200:
                return response.json()

            logger.warning(f"HubSpot get contact failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"HubSpot get contact error: {e}")
            return None

    async def search_contacts(self, email: str) -> list[dict[str, Any]] | None:
        """Search contacts by email.

        Args:
            email: Email to search for

        Returns:
            List of matching contacts
        """
        if not self.api_key:
            logger.warning("HubSpot not configured")
            return None

        try:
            url = f"{self.api_url}/crm/v3/objects/contacts/search"

            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": email,
                            }
                        ]
                    }
                ]
            }

            response = await self.http_client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])

            logger.warning(f"HubSpot search contacts failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"HubSpot search contacts error: {e}")
            return None

    async def create_deal(self, deal_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new deal in HubSpot.

        Args:
            deal_data: Deal data including dealname, amount, pipeline

        Returns:
            Created deal data
        """
        if not self.api_key:
            logger.warning("HubSpot not configured")
            return None

        try:
            url = f"{self.api_url}/crm/v3/objects/deals"

            properties = {
                "dealname": deal_data.get("name"),
                "amount": str(deal_data.get("amount", 0)),
                "pipeline": deal_data.get("pipeline", "default"),
            }

            response = await self.http_client.post(
                url,
                json={"properties": properties},
            )

            if response.status_code in (200, 201):
                return response.json()

            logger.warning(f"HubSpot create deal failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"HubSpot create deal error: {e}")
            return None

    async def create_engagement(
        self,
        engagement_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Create an engagement (note, email, etc.).

        Args:
            engagement_data: Engagement data

        Returns:
            Created engagement data
        """
        if not self.api_key:
            logger.warning("HubSpot not configured")
            return None

        try:
            url = f"{self.api_url}/crm/v3/objects/notes"

            properties = {
                "hs_note_body": engagement_data.get("body"),
                "hs_timestamp": engagement_data.get("timestamp"),
            }

            response = await self.http_client.post(
                url,
                json={"properties": properties},
            )

            if response.status_code in (200, 201):
                return response.json()

            logger.warning(f"HubSpot create engagement failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"HubSpot create engagement error: {e}")
            return None