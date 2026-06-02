"""Initial migration.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial tables."""
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "ACTIVE", "SUSPENDED", "BANNED", "DELETED", name="userstatus"), nullable=False),
        sa.Column("is_email_verified", sa.Boolean(), nullable=False),
        sa.Column("is_phone_verified", sa.Boolean(), nullable=False),
        sa.Column("verification_status", sa.Enum("UNVERIFIED", "PENDING", "VERIFIED", "REJECTED", "EXPIRED", name="userverificationstatus"), nullable=False),
        sa.Column("date_of_birth", sa.DateTime(timezone=True), nullable=True),
        sa.Column("age_verification_method", sa.String(length=50), nullable=True),
        sa.Column("age_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=250), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("short_description", sa.String(length=500), nullable=True),
        sa.Column("category", sa.Enum("ADULT_ENTERTAINMENT", "ESCORT", "MASSAGE", "COMPANION", "DATING", "ADULT_CONTENT", "OTHER", name="listingcategory"), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "PENDING_REVIEW", "ACTIVE", "PAUSED", "SUSPENDED", "REJECTED", "EXPIRED", name="listingstatus"), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("is_premium", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("view_count", sa.Integer(), nullable=False),
        sa.Column("like_count", sa.Integer(), nullable=False),
        sa.Column("review_count", sa.Integer(), nullable=False),
        sa.Column("average_rating", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("price_amount", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("price_currency", sa.String(length=3), nullable=False),
        sa.Column("location_city", sa.String(length=100), nullable=True),
        sa.Column("location_state", sa.String(length=100), nullable=True),
        sa.Column("location_country", sa.String(length=2), nullable=False),
        sa.Column("location_lat", sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column("location_lng", sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column("contact_phone", sa.String(length=20), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("contact_website", sa.String(length=500), nullable=True),
        sa.Column("working_hours", postgresql.JSON(), nullable=True),
        sa.Column("images", postgresql.ARRAY(sa.String(length=500)), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String(length=50)), nullable=True),
        sa.Column("amenities", postgresql.ARRAY(sa.String(length=100)), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_listings_user_id", "listings", ["user_id"])
    op.create_index("ix_listings_slug", "listings", ["slug"], unique=True)
    op.create_index("ix_listings_status", "listings", ["status"])

    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "AUTHORIZED", "CAPTURED", "COMPLETED", "FAILED", "REFUNDED", "PARTIALLY_REFUNDED", "VOIDED", "EXPIRED", name="paymentstatus"), nullable=False),
        sa.Column("payment_method", sa.Enum("CCBILL", "PAXUM", "BANK_TRANSFER", "CRYPTOCURRENCY", "OTHER", name="paymentmethod"), nullable=False),
        sa.Column("payment_type", sa.Enum("SUBSCRIPTION", "LISTING_PROMOTION", "VERIFICATION", "OTHER", name="paymenttype"), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("provider_reference", sa.String(length=255), nullable=True),
        sa.Column("provider_response", postgresql.JSON(), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refunded_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("is_test", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_provider_reference", "payments", ["provider_reference"], unique=True)

    op.create_table(
        "payment_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("provider_reference", sa.String(length=255), nullable=True),
        sa.Column("request_data", postgresql.JSON(), nullable=True),
        sa.Column("response_data", postgresql.JSON(), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payment_transactions_payment_id", "payment_transactions", ["payment_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.Enum("CREATE", "UPDATE", "DELETE", "SOFT_DELETE", "RESTORE", "LOGIN", "LOGOUT", "LOGIN_FAILED", "PASSWORD_CHANGE", "EMAIL_VERIFIED", "PHONE_VERIFIED", "AGE_VERIFIED", "LISTING_PUBLISHED", "LISTING_SUSPENDED", "PAYMENT_INITIATED", "PAYMENT_COMPLETED", "PAYMENT_FAILED", "PAYMENT_REFUNDED", name="auditaction"), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("old_values", postgresql.JSON(), nullable=True),
        sa.Column("new_values", postgresql.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("endpoint", sa.String(length=500), nullable=True),
        sa.Column("method", sa.String(length=10), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_request_id", "audit_logs", ["request_id"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("audit_logs")
    op.drop_table("payment_transactions")
    op.drop_table("payments")
    op.drop_table("listings")
    op.drop_table("users")