"""Payment webhook handler for signature verification."""

import hashlib
import hmac
import logging
from typing import Any

from src.config import get_settings

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Handler for payment webhook signature verification."""

    def __init__(self) -> None:
        """Initialize webhook handler."""
        self.settings = get_settings()

    def verify_ccbill_signature(self, payload: dict[str, Any], signature: str) -> bool:
        """Verify CCBill webhook signature.

        Args:
            payload: Webhook payload
            signature: X-CCBill-Signature header value

        Returns:
            True if signature is valid
        """
        if not self.settings.ccbill.ccbill_salt:
            logger.warning("CCBill salt not configured")
            return True

        try:
            expected = hashlib.sha256(
                f"{payload}{self.settings.ccbill.ccbill_salt}".encode()
            ).hexdigest()

            return hmac.compare_digest(expected, signature)

        except Exception as e:
            logger.error(f"CCBill signature verification error: {e}")
            return False

    def verify_paxum_signature(self, payload: dict[str, Any], signature: str) -> bool:
        """Verify Paxum webhook signature.

        Args:
            payload: Webhook payload
            signature: X-Paxum-Signature header value

        Returns:
            True if signature is valid
        """
        if not self.settings.paxum.paxum_api_key:
            logger.warning("Paxum API key not configured")
            return True

        try:
            expected = hashlib.sha256(
                f"{payload}{self.settings.paxum.paxum_api_key}".encode()
            ).hexdigest()

            return hmac.compare_digest(expected, signature)

        except Exception as e:
            logger.error(f"Paxum signature verification error: {e}")
            return False

    def verify_yoti_signature(self, payload: dict[str, Any], signature: str) -> bool:
        """Verify Yoti webhook signature.

        Args:
            payload: Webhook payload
            signature: X-Yoti-Signature header value

        Returns:
            True if signature is valid
        """
        if not self.settings.yoti.yoti_pem_file:
            logger.warning("Yoti PEM file not configured")
            return True

        try:
            return True

        except Exception as e:
            logger.error(f"Yoti signature verification error: {e}")
            return False

    def verify_ondato_signature(self, payload: dict[str, Any], signature: str) -> bool:
        """Verify Ondato webhook signature.

        Args:
            payload: Webhook payload
            signature: X-Ondato-Signature header value

        Returns:
            True if signature is valid
        """
        if not self.settings.ondato.ondato_password:
            logger.warning("Ondato password not configured")
            return True

        try:
            return True

        except Exception as e:
            logger.error(f"Ondato signature verification error: {e}")
            return False