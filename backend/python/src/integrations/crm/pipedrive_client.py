"""Pipedrive CRM client."""

import logging
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class PipedriveClient:
    """Pipedrive CRM API client."""

    def __init__(self) -> None:
        """Initialize Pipedrive client."""
        self.settings = get_settings()
        self.api_token = self.settings.pipedrive.pipedrive_api_token
        self.api_url = self.settings.pipedrive.pipedrive_api_url
        self._http_client: httpx.AsyncClient | None = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                params={"api_token": self.api_token} if self.api_token else {},
            )
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def create_person(self, person_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new person in Pipedrive.

        Args:
            person_data: Person data including name, email, phone

        Returns:
            Created person data
        """
        if not self.api_token:
            logger.warning("Pipedrive not configured")
            return None

        try:
            url = f"{self.api_url}/v1/persons"

            response = await self.http_client.post(url, json=person_data)

            if response.status_code in (200, 201):
                data = response.json()
                return data.get("data")

            logger.warning(f"Pipedrive create person failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Pipedrive create person error: {e}")
            return None

    async def update_person(self, person_id: int, person_data: dict[str, Any]) -> dict[str, Any] | None:
        """Update a person in Pipedrive.

        Args:
            person_id: Person ID
            person_data: Updated person data

        Returns:
            Updated person data
        """
        if not self.api_token:
            logger.warning("Pipedrive not configured")
            return None

        try:
            url = f"{self.api_url}/v1/persons/{person_id}"

            response = await self.http_client.put(url, json=person_data)

            if response.status_code == 200:
                data = response.json()
                return data.get("data")

            logger.warning(f"Pipedrive update person failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Pipedrive update person error: {e}")
            return None

    async def create_deal(self, deal_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new deal in Pipedrive.

        Args:
            deal_data: Deal data including title, value, currency

        Returns:
            Created deal data
        """
        if not self.api_token:
            logger.warning("Pipedrive not configured")
            return None

        try:
            url = f"{self.api_url}/v1/deals"

            response = await self.http_client.post(url, json=deal_data)

            if response.status_code in (200, 201):
                data = response.json()
                return data.get("data")

            logger.warning(f"Pipedrive create deal failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Pipedrive create deal error: {e}")
            return None

    async def add_note_to_deal(self, deal_id: int, content: str) -> dict[str, Any] | None:
        """Add a note to a deal.

        Args:
            deal_id: Deal ID
            content: Note content

        Returns:
            Created note data
        """
        if not self.api_token:
            logger.warning("Pipedrive not configured")
            return None

        try:
            url = f"{self.api_url}/v1/notes"

            payload = {
                "content": content,
                "deal_id": deal_id,
            }

            response = await self.http_client.post(url, json=payload)

            if response.status_code in (200, 201):
                data = response.json()
                return data.get("data")

            logger.warning(f"Pipedrive add note failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Pipedrive add note error: {e}")
            return None

    async def search_persons(self, email: str) -> list[dict[str, Any]] | None:
        """Search for persons by email.

        Args:
            email: Email to search for

        Returns:
            List of matching persons
        """
        if not self.api_token:
            logger.warning("Pipedrive not configured")
            return None

        try:
            url = f"{self.api_url}/v1/persons/search"
            params = {
                "term": email,
                "fields": "email",
                "exact_match": True,
            }

            response = await self.http_client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("items", [])

            logger.warning(f"Pipedrive search persons failed: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Pipedrive search persons error: {e}")
            return None