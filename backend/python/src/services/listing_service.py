"""Listing service with business logic."""

import logging
import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from src.models.listing import Listing, ListingStatus, ListingCategory
from src.schemas.listing import (
    ListingCreate,
    ListingUpdate,
    ListingSearchQuery,
)
from src.models.user import User, UserVerificationStatus
from src.processing.search_indexer import SearchIndexer
from src.workers.tasks import index_listing_task

logger = logging.getLogger(__name__)


def generate_slug(title: str, listing_id: uuid.UUID) -> str:
    """Generate URL-friendly slug from title."""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    slug = slug.strip("-")
    unique_part = str(listing_id)[:8]
    return f"{slug}-{unique_part}"


class ListingService:
    """Service class for listing operations."""

    def __init__(self, db: Session) -> None:
        """Initialize listing service."""
        self.db = db
        self.search_indexer = SearchIndexer()

    async def get_listing_by_id(self, listing_id: str) -> Listing | None:
        """Get listing by ID."""
        try:
            listing_uuid = uuid.UUID(listing_id)
        except ValueError:
            return None

        return self.db.query(Listing).filter(
            Listing.id == listing_uuid,
            Listing.is_deleted == False,  # noqa: E712
        ).first()

    async def get_listing_by_slug(self, slug: str) -> Listing | None:
        """Get listing by slug."""
        return self.db.query(Listing).filter(
            Listing.slug == slug,
            Listing.is_deleted == False,  # noqa: E712
        ).first()

    async def create_listing(self, listing_data: ListingCreate, user_id: uuid.UUID) -> Listing:
        """Create a new listing."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        listing = Listing(
            user_id=user_id,
            title=listing_data.title,
            description=listing_data.description,
            short_description=listing_data.short_description,
            category=ListingCategory(listing_data.category),
            status=ListingStatus.DRAFT,
            price_amount=listing_data.price_amount,
            price_currency=listing_data.price_currency,
            location_city=listing_data.location_city,
            location_state=listing_data.location_state,
            location_country=listing_data.location_country,
            location_lat=listing_data.location_lat,
            location_lng=listing_data.location_lng,
            contact_phone=listing_data.contact_phone,
            contact_email=listing_data.contact_email,
            contact_website=listing_data.contact_website,
            working_hours=listing_data.working_hours,
            tags=listing_data.tags,
            amenities=listing_data.amenities,
        )

        self.db.add(listing)
        self.db.flush()

        listing.slug = generate_slug(listing.title, listing.id)

        self.db.commit()
        self.db.refresh(listing)

        logger.info(f"Created new listing: {listing.id}")
        return listing

    async def update_listing(
        self,
        listing_id: str,
        listing_data: ListingUpdate,
    ) -> Listing | None:
        """Update listing by ID."""
        listing = await self.get_listing_by_id(listing_id)
        if not listing:
            return None

        update_data = listing_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "category" and value:
                setattr(listing, field, ListingCategory(value))
            elif field == "status" and value:
                setattr(listing, field, ListingStatus(value))
            else:
                setattr(listing, field, value)

        if listing.title:
            listing.slug = generate_slug(listing.title, listing.id)

        self.db.commit()
        self.db.refresh(listing)

        index_listing_task.delay(str(listing.id))

        logger.info(f"Updated listing: {listing.id}")
        return listing

    async def delete_listing(self, listing_id: str) -> bool:
        """Soft delete listing by ID."""
        listing = await self.get_listing_by_id(listing_id)
        if not listing:
            return False

        listing.is_deleted = True
        listing.deleted_at = datetime.now(timezone.utc)

        self.db.commit()

        logger.info(f"Soft deleted listing: {listing.id}")
        return True

    async def search_listings(self, query: ListingSearchQuery) -> dict:
        """Search listings with filters."""
        db_query = self.db.query(Listing).filter(
            Listing.status == ListingStatus.ACTIVE,
            Listing.is_deleted == False,  # noqa: E712
        )

        if query.query:
            search_term = f"%{query.query}%"
            db_query = db_query.filter(
                or_(
                    Listing.title.ilike(search_term),
                    Listing.description.ilike(search_term),
                )
            )

        if query.category:
            try:
                category = ListingCategory(query.category)
                db_query = db_query.filter(Listing.category == category)
            except ValueError:
                pass

        if query.location_country:
            db_query = db_query.filter(Listing.location_country == query.location_country)

        if query.location_city:
            db_query = db_query.filter(Listing.location_city == query.location_city)

        if query.min_price is not None:
            db_query = db_query.filter(Listing.price_amount >= query.min_price)

        if query.max_price is not None:
            db_query = db_query.filter(Listing.price_amount <= query.max_price)

        if query.is_verified is not None:
            db_query = db_query.filter(Listing.is_verified == query.is_verified)

        if query.is_premium is not None:
            db_query = db_query.filter(Listing.is_premium == query.is_premium)

        if query.sort_by == "price":
            order_col = Listing.price_amount
        elif query.sort_by == "rating":
            order_col = Listing.average_rating
        elif query.sort_by == "popular":
            order_col = Listing.view_count
        else:
            order_col = Listing.created_at

        if query.sort_order == "asc":
            db_query = db_query.order_by(order_col.asc())
        else:
            db_query = db_query.order_by(order_col.desc())

        total = db_query.count()

        listings = db_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()

        total_pages = (total + query.page_size - 1) // query.page_size

        return {
            "items": listings,
            "total": total,
            "page": query.page,
            "page_size": query.page_size,
            "total_pages": total_pages,
        }

    async def get_user_listings(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> dict:
        """Get all listings for a specific user."""
        query = self.db.query(Listing).filter(
            Listing.user_id == uuid.UUID(user_id),
            Listing.is_deleted == False,  # noqa: E712
        )

        if status:
            try:
                status_enum = ListingStatus(status)
                query = query.filter(Listing.status == status_enum)
            except ValueError:
                pass

        total = query.count()

        listings = query.offset((page - 1) * page_size).limit(page_size).all()

        total_pages = (total + page_size - 1) // page_size

        return {
            "items": listings,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def update_status(
        self,
        listing_id: str,
        status: str,
        rejection_reason: str | None = None,
    ) -> Listing | None:
        """Update listing status."""
        listing = await self.get_listing_by_id(listing_id)
        if not listing:
            return None

        try:
            new_status = ListingStatus(status)
            listing.status = new_status

            if new_status == ListingStatus.ACTIVE:
                listing.activated_at = datetime.now(timezone.utc)
            elif new_status == ListingStatus.REJECTED:
                listing.rejection_reason = rejection_reason

            self.db.commit()
            self.db.refresh(listing)

            logger.info(f"Listing status updated: {listing.id} -> {status}")
            return listing
        except ValueError:
            return None

    async def publish_listing(self, listing_id: str) -> Listing | None:
        """Submit listing for review/publishing."""
        listing = await self.get_listing_by_id(listing_id)
        if not listing:
            return None

        user = self.db.query(User).filter(User.id == listing.user_id).first()
        if not user or user.verification_status != UserVerificationStatus.VERIFIED:
            logger.warning(f"Cannot publish listing {listing_id}: user not verified")
            return None

        if not listing.title or not listing.description or not listing.location_country:
            logger.warning(f"Cannot publish listing {listing_id}: missing required fields")
            return None

        listing.status = ListingStatus.PENDING_REVIEW
        self.db.commit()
        self.db.refresh(listing)

        logger.info(f"Listing submitted for review: {listing.id}")
        return listing

    async def pause_listing(self, listing_id: str) -> Listing | None:
        """Pause an active listing."""
        listing = await self.get_listing_by_id(listing_id)
        if not listing:
            return None

        if listing.status != ListingStatus.ACTIVE:
            return None

        listing.status = ListingStatus.PAUSED
        self.db.commit()
        self.db.refresh(listing)

        logger.info(f"Listing paused: {listing.id}")
        return listing

    async def increment_view_count(self, listing_id: str) -> None:
        """Increment listing view count."""
        listing = await self.get_listing_by_id(listing_id)
        if listing:
            listing.view_count += 1
            self.db.commit()