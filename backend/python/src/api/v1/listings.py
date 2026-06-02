"""Listings API router."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.listing import (
    ListingCreate,
    ListingUpdate,
    ListingResponse,
    ListingListResponse,
    ListingSearchQuery,
    ListingStatusUpdate,
)
from src.services.listing_service import ListingService
from src.middleware.auth import get_current_user
from src.models.user import User
from src.models.listing import Listing

router = APIRouter()


def get_listing_service(db: Session = Depends(get_db)) -> ListingService:
    """Get listing service instance."""
    return ListingService(db)


@router.post("", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: ListingCreate,
    service: Annotated[ListingService, Depends(get_listing_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Listing:
    """Create a new listing."""
    listing = await service.create_listing(listing_data, current_user.id)
    return listing


@router.get("/search", response_model=ListingListResponse)
async def search_listings(
    service: Annotated[ListingService, Depends(get_listing_service)],
    query: str | None = None,
    category: str | None = None,
    location_country: str | None = None,
    location_city: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    is_verified: bool | None = None,
    is_premium: bool | None = None,
    sort_by: str = Query(default="created_at", pattern=r"^(created_at|price|rating|popular)$"),
    sort_order: str = Query(default="desc", pattern=r"^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    """Search listings with filters."""
    search_query = ListingSearchQuery(
        query=query,
        category=category,
        location_country=location_country,
        location_city=location_city,
        min_price=min_price,
        max_price=max_price,
        is_verified=is_verified,
        is_premium=is_premium,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return await service.search_listings(search_query)


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    service: Annotated[ListingService, Depends(get_listing_service)],
) -> Listing:
    """Get listing by ID."""
    listing = await service.get_listing_by_id(listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    await service.increment_view_count(listing_id)
    return listing


@router.get("/slug/{slug}", response_model=ListingResponse)
async def get_listing_by_slug(
    slug: str,
    service: Annotated[ListingService, Depends(get_listing_service)],
) -> Listing:
    """Get listing by slug."""
    listing = await service.get_listing_by_slug(slug)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    await service.increment_view_count(listing.id)
    return listing


@router.patch("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: str,
    listing_data: ListingUpdate,
    service: Annotated[ListingService, Depends(get_listing_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Listing:
    """Update listing by ID."""
    listing = await service.get_listing_by_id(listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    if str(listing.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this listing",
        )

    updated_listing = await service.update_listing(listing_id, listing_data)
    return updated_listing


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: str,
    service: Annotated[ListingService, Depends(get_listing_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Soft delete listing by ID."""
    listing = await service.get_listing_by_id(listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    if str(listing.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this listing",
        )

    await service.delete_listing(listing_id)


@router.patch("/{listing_id}/status", response_model=ListingResponse)
async def update_listing_status(
    listing_id: str,
    status_data: ListingStatusUpdate,
    service: Annotated[ListingService, Depends(get_listing_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Listing:
    """Update listing status (admin only in production)."""
    listing = await service.update_status(listing_id, status_data.status, status_data.rejection_reason)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )
    return listing


@router.post("/{listing_id}/publish", response_model=ListingResponse)
async def publish_listing(
    listing_id: str,
    service: Annotated[ListingService, Depends(get_listing_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Listing:
    """Submit listing for review/publishing."""
    listing = await service.get_listing_by_id(listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    if str(listing.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this listing",
        )

    published_listing = await service.publish_listing(listing_id)
    if not published_listing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Listing cannot be published. Ensure all required fields are filled.",
        )
    return published_listing


@router.post("/{listing_id}/pause", response_model=ListingResponse)
async def pause_listing(
    listing_id: str,
    service: Annotated[ListingService, Depends(get_listing_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Listing:
    """Pause an active listing."""
    listing = await service.get_listing_by_id(listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    if str(listing.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pause this listing",
        )

    paused_listing = await service.pause_listing(listing_id)
    return paused_listing


@router.get("/user/{user_id}", response_model=ListingListResponse)
async def get_user_listings(
    user_id: str,
    service: Annotated[ListingService, Depends(get_listing_service)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = None,
) -> dict:
    """Get all listings for a specific user."""
    return await service.get_user_listings(
        user_id=user_id,
        page=page,
        page_size=page_size,
        status=status,
    )