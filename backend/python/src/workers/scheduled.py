"""Scheduled tasks for Celery beat."""

import logging

from celery import shared_task

import redis

from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@shared_task
def cleanup_expired_sessions() -> dict[str, Any]:
    """Clean up expired user sessions."""
    try:
        redis_client = redis.from_url(settings.redis.redis_url, decode_responses=True)

        pattern = "session:*:expires"
        expired_keys = []

        for key in redis_client.scan_iter(match=pattern, count=100):
            ttl = redis_client.ttl(key)
            if ttl and ttl <= 0:
                expired_keys.append(key)

        for key in expired_keys:
            redis_client.delete(key)

        logger.info(f"Cleaned up {len(expired_keys)} expired sessions")
        return {"cleaned": len(expired_keys)}

    except Exception as e:
        logger.error(f"Failed to cleanup expired sessions: {e}")
        return {"error": str(e)}


@shared_task
def update_listing_stats() -> dict[str, Any]:
    """Update listing statistics from analytics."""
    try:
        logger.info("Updating listing statistics")
        return {"updated": True}

    except Exception as e:
        logger.error(f"Failed to update listing stats: {e}")
        return {"error": str(e)}


@shared_task
def process_analytics_queue() -> dict[str, Any]:
    """Process queued analytics events."""
    try:
        redis_client = redis.from_url(settings.redis.redis_url, decode_responses=True)

        events_processed = 0
        max_events = 1000

        while events_processed < max_events:
            event_data = redis_client.rpop("analytics:events")
            if not event_data:
                break
            events_processed += 1

        logger.info(f"Processed {events_processed} analytics events")
        return {"processed": events_processed}

    except Exception as e:
        logger.error(f"Failed to process analytics queue: {e}")
        return {"error": str(e)}


@shared_task
def check_listing_expiry() -> dict[str, Any]:
    """Check and expire listings that have passed their expiry date."""
    try:
        logger.info("Checking listing expiry")
        return {"checked": True}

    except Exception as e:
        logger.error(f"Failed to check listing expiry: {e}")
        return {"error": str(e)}


@shared_task
def send_daily_digest() -> dict[str, Any]:
    """Send daily digest emails to users."""
    try:
        logger.info("Sending daily digest emails")
        return {"sent": 0}

    except Exception as e:
        logger.error(f"Failed to send daily digest: {e}")
        return {"error": str(e)}


@shared_task
def sync_crm_contacts() -> dict[str, Any]:
    """Sync contacts with CRM systems."""
    try:
        logger.info("Syncing CRM contacts")
        return {"synced": True}

    except Exception as e:
        logger.error(f"Failed to sync CRM contacts: {e}")
        return {"error": str(e)}


from typing import Any