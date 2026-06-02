"""Background tasks for Celery workers."""

import logging
from typing import Any

from celery import shared_task

from src.services.notification_service import NotificationService
from src.processing.search_indexer import SearchIndexer
from src.processing.image_processor import ImageProcessor
from src.models.payment import Payment

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email(
    self: Any,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str | None = None,
) -> bool:
    """Send an email notification.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML email body
        text_body: Optional plain text body

    Returns:
        True if email sent successfully
    """
    try:
        service = NotificationService()
        result = service.send_email(to_email, subject, html_body, text_body)
        return result
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_payment(
    self: Any,
    payment_id: str,
    action: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Process a payment action.

    Args:
        payment_id: Payment ID
        action: Action to perform (capture, refund, void)
        **kwargs: Additional action-specific parameters

    Returns:
        Processing result
    """
    try:
        logger.info(f"Processing payment {payment_id}, action: {action}")

        if action == "capture":
            return {"status": "success", "payment_id": payment_id}
        elif action == "refund":
            return {"status": "success", "payment_id": payment_id, "refunded": True}
        elif action == "void":
            return {"status": "success", "payment_id": payment_id, "voided": True}
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    except Exception as e:
        logger.error(f"Failed to process payment {payment_id}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def index_listing(self: Any, listing_id: str, operation: str = "index") -> bool:
    """Index or update a listing in search engine.

    Args:
        listing_id: Listing ID
        operation: Operation type (index, update, delete)

    Returns:
        True if indexing successful
    """
    try:
        indexer = SearchIndexer()

        if operation == "index":
            return await indexer.index_listing({"id": listing_id})
        elif operation == "update":
            return await indexer.update_listing(listing_id, {"id": listing_id})
        elif operation == "delete":
            return await indexer.delete_listing(listing_id)
        else:
            return False

    except Exception as e:
        logger.error(f"Failed to {operation} listing {listing_id}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_image(
    self: Any,
    image_url: str,
    listing_id: str,
    operation: str = "process",
) -> dict[str, Any] | None:
    """Process an image for a listing.

    Args:
        image_url: URL of the image
        listing_id: Listing ID
        operation: Operation type (process, optimize)

    Returns:
        Processed image data or None if failed
    """
    try:
        processor = ImageProcessor()

        if operation == "process":
            return await processor.process_image_from_url(image_url)
        elif operation == "optimize":
            return await processor.get_image_metadata(image_url)
        else:
            return None

    except Exception as e:
        logger.error(f"Failed to {operation} image for listing {listing_id}: {e}")
        raise self.retry(exc=e)


@shared_task
def send_welcome_email(user_id: str, email: str, first_name: str | None = None) -> bool:
    """Send welcome email to new user.

    Args:
        user_id: User ID
        email: User email
        first_name: Optional first name

    Returns:
        True if email sent successfully
    """
    try:
        service = NotificationService()
        return service.send_welcome_email(email, first_name)
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {e}")
        return False


@shared_task
def send_payment_confirmation(
    email: str,
    payment_details: dict[str, Any],
) -> bool:
    """Send payment confirmation email.

    Args:
        email: User email
        payment_details: Payment details dictionary

    Returns:
        True if email sent successfully
    """
    try:
        service = NotificationService()
        return service.send_payment_confirmation_email(email, payment_details)
    except Exception as e:
        logger.error(f"Failed to send payment confirmation to {email}: {e}")
        return False


@shared_task
def send_listing_notification(
    email: str,
    listing_title: str,
    notification_type: str,
    **kwargs: Any,
) -> bool:
    """Send listing-related notification.

    Args:
        email: User email
        listing_title: Listing title
        notification_type: Type of notification (approved, rejected, etc.)
        **kwargs: Additional parameters

    Returns:
        True if email sent successfully
    """
    try:
        service = NotificationService()

        if notification_type == "approved":
            listing_url = kwargs.get("listing_url", "")
            return service.send_listing_approved_email(email, listing_title, listing_url)
        elif notification_type == "rejected":
            rejection_reason = kwargs.get("rejection_reason", "Please review your listing")
            return service.send_listing_rejected_email(email, listing_title, rejection_reason)
        else:
            return False

    except Exception as e:
        logger.error(f"Failed to send listing notification to {email}: {e}")
        return False


@shared_task
def bulk_index_listings(listing_ids: list[str]) -> dict[str, Any]:
    """Bulk index multiple listings.

    Args:
        listing_ids: List of listing IDs

    Returns:
        Bulk operation results
    """
    try:
        indexer = SearchIndexer()
        listings = [{"id": lid} for lid in listing_ids]
        return indexer.bulk_index(listings)
    except Exception as e:
        logger.error(f"Bulk indexing failed: {e}")
        return {"success": False, "error": str(e)}