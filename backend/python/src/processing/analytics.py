"""Analytics event processing service."""

import logging
from datetime import datetime, timezone
from typing import Any

import redis

from src.config import get_settings

logger = logging.getLogger(__name__)


class AnalyticsProcessor:
    """Service for processing analytics events."""

    def __init__(self) -> None:
        """Initialize analytics processor."""
        self.settings = get_settings()
        self._redis_client: redis.Redis | None = None

    @property
    def redis_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(
                self.settings.redis.redis_url,
                decode_responses=True,
            )
        return self._redis_client

    def close(self) -> None:
        """Close Redis client."""
        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None

    def track_event(
        self,
        event_type: str,
        user_id: str | None = None,
        listing_id: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> bool:
        """Track an analytics event.

        Args:
            event_type: Type of event
            user_id: Optional user ID
            listing_id: Optional listing ID
            properties: Optional event properties

        Returns:
            True if tracking successful
        """
        try:
            event = {
                "type": event_type,
                "user_id": user_id,
                "listing_id": listing_id,
                "properties": properties or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            self.redis_client.lpush("analytics:events", str(event))
            return True

        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return False

    def track_page_view(
        self,
        user_id: str | None,
        page_url: str,
        referrer: str | None = None,
    ) -> bool:
        """Track a page view.

        Args:
            user_id: Optional user ID
            page_url: Page URL
            referrer: Optional referrer URL

        Returns:
            True if tracking successful
        """
        return self.track_event(
            event_type="page_view",
            user_id=user_id,
            properties={
                "url": page_url,
                "referrer": referrer,
            },
        )

    def track_listing_view(self, user_id: str | None, listing_id: str) -> bool:
        """Track a listing view.

        Args:
            user_id: Optional user ID
            listing_id: Listing ID

        Returns:
            True if tracking successful
        """
        return self.track_event(
            event_type="listing_view",
            user_id=user_id,
            listing_id=listing_id,
        )

    def track_listing_click(
        self,
        user_id: str | None,
        listing_id: str,
        click_type: str,
    ) -> bool:
        """Track a listing click.

        Args:
            user_id: Optional user ID
            listing_id: Listing ID
            click_type: Type of click (phone, email, website)

        Returns:
            True if tracking successful
        """
        return self.track_event(
            event_type="listing_click",
            user_id=user_id,
            listing_id=listing_id,
            properties={"click_type": click_type},
        )

    def track_search(
        self,
        user_id: str | None,
        search_query: str,
        results_count: int,
    ) -> bool:
        """Track a search event.

        Args:
            user_id: Optional user ID
            search_query: Search query string
            results_count: Number of results

        Returns:
            True if tracking successful
        """
        return self.track_event(
            event_type="search",
            user_id=user_id,
            properties={
                "query": search_query,
                "results_count": results_count,
            },
        )

    def track_signup(self, user_id: str, signup_method: str) -> bool:
        """Track a user signup.

        Args:
            user_id: User ID
            signup_method: Signup method (email, google, apple)

        Returns:
            True if tracking successful
        """
        return self.track_event(
            event_type="signup",
            user_id=user_id,
            properties={"method": signup_method},
        )

    def track_payment(
        self,
        user_id: str,
        payment_id: str,
        amount: float,
        currency: str,
        payment_method: str,
    ) -> bool:
        """Track a payment event.

        Args:
            user_id: User ID
            payment_id: Payment ID
            amount: Payment amount
            currency: Currency code
            payment_method: Payment method used

        Returns:
            True if tracking successful
        """
        return self.track_event(
            event_type="payment",
            user_id=user_id,
            properties={
                "payment_id": payment_id,
                "amount": amount,
                "currency": currency,
                "payment_method": payment_method,
            },
        )

    def get_listing_stats(self, listing_id: str) -> dict[str, Any]:
        """Get statistics for a listing.

        Args:
            listing_id: Listing ID

        Returns:
            Listing statistics
        """
        try:
            views = self.redis_client.get(f"listing:{listing_id}:views")
            clicks = self.redis_client.get(f"listing:{listing_id}:clicks")

            return {
                "listing_id": listing_id,
                "views": int(views) if views else 0,
                "clicks": int(clicks) if clicks else 0,
            }

        except Exception as e:
            logger.error(f"Failed to get listing stats: {e}")
            return {
                "listing_id": listing_id,
                "views": 0,
                "clicks": 0,
                "error": str(e),
            }

    def get_user_stats(self, user_id: str) -> dict[str, Any]:
        """Get statistics for a user.

        Args:
            user_id: User ID

        Returns:
            User statistics
        """
        try:
            searches = self.redis_client.get(f"user:{user_id}:searches")
            listings_created = self.redis_client.get(f"user:{user_id}:listings_created")
            payments = self.redis_client.get(f"user:{user_id}:payments")

            return {
                "user_id": user_id,
                "searches": int(searches) if searches else 0,
                "listings_created": int(listings_created) if listings_created else 0,
                "payments": int(payments) if payments else 0,
            }

        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {
                "user_id": user_id,
                "searches": 0,
                "listings_created": 0,
                "payments": 0,
                "error": str(e),
            }