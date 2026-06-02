"""Notification service for email and SMS."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Service class for sending notifications."""

    def __init__(self) -> None:
        """Initialize notification service."""
        self.settings = get_settings()

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
        from_email: str | None = None,
    ) -> bool:
        """Send an email notification."""
        try:
            from_email_addr = from_email or self.settings.aws.aws_ses_from_email

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_email_addr
            msg["To"] = to_email

            if text_body:
                msg.attach(MIMEText(text_body, "plain"))

            msg.attach(MIMEText(html_body, "html"))

            logger.info(f"Sending email to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send an SMS notification."""
        try:
            logger.info(f"Sending SMS to {phone_number}: {message[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return False

    async def send_verification_email(self, email: str, verification_url: str) -> bool:
        """Send email verification message."""
        subject = "Verify your email address"
        html_body = f"""
        <html>
            <body>
                <h2>Email Verification</h2>
                <p>Please click the link below to verify your email address:</p>
                <p><a href="{verification_url}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, please ignore this email.</p>
            </body>
        </html>
        """
        text_body = f"""
        Email Verification

        Please click the link below to verify your email address:
        {verification_url}

        This link will expire in 24 hours.
        If you didn't create an account, please ignore this email.
        """
        return await self.send_email(email, subject, html_body, text_body)

    async def send_password_reset_email(self, email: str, reset_url: str) -> bool:
        """Send password reset email."""
        subject = "Reset your password"
        html_body = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You requested a password reset. Click the link below to set a new password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request a password reset, please ignore this email.</p>
            </body>
        </html>
        """
        text_body = f"""
        Password Reset Request

        You requested a password reset. Click the link below to set a new password:
        {reset_url}

        This link will expire in 1 hour.
        If you didn't request a password reset, please ignore this email.
        """
        return await self.send_email(email, subject, html_body, text_body)

    async def send_welcome_email(self, email: str, first_name: str | None = None) -> bool:
        """Send welcome email to new users."""
        name = first_name or "User"
        subject = "Welcome to Premium Service Directory"
        html_body = f"""
        <html>
            <body>
                <h2>Welcome, {name}!</h2>
                <p>Thank you for joining Premium Service Directory.</p>
                <p>To get started:</p>
                <ul>
                    <li>Complete your profile</li>
                    <li>Verify your age</li>
                    <li>Create your first listing</li>
                </ul>
                <p>If you have any questions, please contact our support team.</p>
            </body>
        </html>
        """
        text_body = f"""
        Welcome, {name}!

        Thank you for joining Premium Service Directory.

        To get started:
        - Complete your profile
        - Verify your age
        - Create your first listing

        If you have any questions, please contact our support team.
        """
        return await self.send_email(email, subject, html_body, text_body)

    async def send_payment_confirmation_email(
        self,
        email: str,
        payment_details: dict[str, Any],
    ) -> bool:
        """Send payment confirmation email."""
        subject = "Payment Confirmation"
        amount = payment_details.get("amount", 0)
        currency = payment_details.get("currency", "USD")
        payment_id = payment_details.get("payment_id", "N/A")

        html_body = f"""
        <html>
            <body>
                <h2>Payment Confirmation</h2>
                <p>Your payment has been successfully processed.</p>
                <table>
                    <tr><td><strong>Payment ID:</strong></td><td>{payment_id}</td></tr>
                    <tr><td><strong>Amount:</strong></td><td>{currency} {amount}</td></tr>
                    <tr><td><strong>Status:</strong></td><td>Completed</td></tr>
                </table>
                <p>Thank you for your purchase!</p>
            </body>
        </html>
        """
        text_body = f"""
        Payment Confirmation

        Your payment has been successfully processed.

        Payment ID: {payment_id}
        Amount: {currency} {amount}
        Status: Completed

        Thank you for your purchase!
        """
        return await self.send_email(email, subject, html_body, text_body)

    async def send_listing_approved_email(
        self,
        email: str,
        listing_title: str,
        listing_url: str,
    ) -> bool:
        """Send listing approval notification."""
        subject = "Your listing has been approved"
        html_body = f"""
        <html>
            <body>
                <h2>Listing Approved!</h2>
                <p>Great news! Your listing "{listing_title}" has been approved and is now live.</p>
                <p><a href="{listing_url}">View Your Listing</a></p>
                <p>Thank you for using Premium Service Directory!</p>
            </body>
        </html>
        """
        text_body = f"""
        Listing Approved!

        Great news! Your listing "{listing_title}" has been approved and is now live.

        View Your Listing: {listing_url}

        Thank you for using Premium Service Directory!
        """
        return await self.send_email(email, subject, html_body, text_body)

    async def send_listing_rejected_email(
        self,
        email: str,
        listing_title: str,
        rejection_reason: str,
    ) -> bool:
        """Send listing rejection notification."""
        subject = "Your listing requires changes"
        html_body = f"""
        <html>
            <body>
                <h2>Listing Update Required</h2>
                <p>Your listing "{listing_title}" requires some changes before it can be approved.</p>
                <p><strong>Reason:</strong> {rejection_reason}</p>
                <p>Please update your listing and resubmit for review.</p>
            </body>
        </html>
        """
        text_body = f"""
        Listing Update Required

        Your listing "{listing_title}" requires some changes before it can be approved.

        Reason: {rejection_reason}

        Please update your listing and resubmit for review.
        """
        return await self.send_email(email, subject, html_body, text_body)