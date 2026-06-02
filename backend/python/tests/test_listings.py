"""Tests for listings API."""

import pytest
from fastapi.testclient import TestClient

from src.models.listing import Listing, ListingStatus


class TestListingsAPI:
    """Test cases for listings endpoints."""

    def test_create_listing_success(
        self,
        client: TestClient,
        test_user,
        auth_headers: dict,
        sample_listing_data: dict,
    ) -> None:
        """Test successful listing creation."""
        response = client.post(
            "/api/v1/listings",
            json=sample_listing_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_listing_data["title"]
        assert "id" in data
        assert "slug" in data

    def test_create_listing_unauthorized(
        self, client: TestClient, sample_listing_data: dict
    ) -> None:
        """Test listing creation without authentication."""
        response = client.post("/api/v1/listings", json=sample_listing_data)

        assert response.status_code == 401

    def test_create_listing_invalid_data(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Test listing creation with invalid data."""
        invalid_data = {
            "title": "Short",
            "description": "Too short",
            "category": "invalid",
        }

        response = client.post(
            "/api/v1/listings",
            json=invalid_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_get_listing_by_id(
        self, client: TestClient, test_listing: Listing
    ) -> None:
        """Test getting listing by ID."""
        response = client.get(f"/api/v1/listings/{test_listing.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_listing.id)
        assert data["title"] == test_listing.title

    def test_get_listing_not_found(self, client: TestClient) -> None:
        """Test getting non-existent listing."""
        response = client.get("/api/v1/listings/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404

    def test_get_listing_by_slug(
        self, client: TestClient, test_listing: Listing
    ) -> None:
        """Test getting listing by slug."""
        response = client.get(f"/api/v1/listings/slug/{test_listing.slug}")

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == test_listing.slug

    def test_update_listing_success(
        self,
        client: TestClient,
        test_user,
        test_listing: Listing,
        auth_headers: dict,
    ) -> None:
        """Test successful listing update."""
        update_data = {
            "title": "Updated Listing Title Here",
            "price_amount": 200.00,
        }

        response = client.patch(
            f"/api/v1/listings/{test_listing.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Listing Title Here"
        assert float(data["price_amount"]) == 200.00

    def test_update_listing_forbidden(
        self,
        client: TestClient,
        test_listing: Listing,
    ) -> None:
        """Test updating another user's listing."""
        update_data = {"title": "Hacked Title"}

        response = client.patch(
            f"/api/v1/listings/{test_listing.id}",
            json=update_data,
            headers={"Authorization": "Bearer wrong-token"},
        )

        assert response.status_code in [401, 403]

    def test_delete_listing_success(
        self,
        client: TestClient,
        test_user,
        test_listing: Listing,
        auth_headers: dict,
    ) -> None:
        """Test successful listing deletion."""
        response = client.delete(
            f"/api/v1/listings/{test_listing.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    def test_search_listings(
        self, client: TestClient, test_listing: Listing
    ) -> None:
        """Test searching listings."""
        response = client.get(
            "/api/v1/listings/search?query=Test&location_country=US"
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    def test_search_listings_with_filters(
        self, client: TestClient, test_listing: Listing
    ) -> None:
        """Test searching listings with multiple filters."""
        response = client.get(
            "/api/v1/listings/search?"
            "category=escort&"
            "location_country=US&"
            "min_price=50&"
            "max_price=200&"
            "is_verified=false&"
            "sort_by=price&"
            "sort_order=asc"
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_user_listings(
        self, client: TestClient, test_user, test_listing: Listing
    ) -> None:
        """Test getting user's listings."""
        response = client.get(f"/api/v1/listings/user/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert all(item["user_id"] == str(test_user.id) for item in data["items"])


class TestListingStatus:
    """Test cases for listing status operations."""

    def test_publish_listing(
        self,
        client: TestClient,
        test_user,
        test_listing: Listing,
        auth_headers: dict,
    ) -> None:
        """Test publishing a listing."""
        response = client.post(
            f"/api/v1/listings/{test_listing.id}/publish",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == ListingStatus.PENDING_REVIEW.value

    def test_pause_listing(
        self,
        client: TestClient,
        test_user,
        test_listing: Listing,
        auth_headers: dict,
    ) -> None:
        """Test pausing a listing."""
        response = client.post(
            f"/api/v1/listings/{test_listing.id}/pause",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == ListingStatus.PAUSED.value

    def test_update_listing_status_admin(
        self,
        client: TestClient,
        test_listing: Listing,
        auth_headers: dict,
    ) -> None:
        """Test admin updating listing status."""
        status_data = {
            "status": ListingStatus.SUSPENDED.value,
            "rejection_reason": "Policy violation",
        }

        response = client.patch(
            f"/api/v1/listings/{test_listing.id}/status",
            json=status_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == ListingStatus.SUSPENDED.value
        assert data["rejection_reason"] == "Policy violation"


class TestListingValidation:
    """Test cases for listing validation."""

    def test_title_too_short(self, client: TestClient, auth_headers: dict) -> None:
        """Test listing with too short title."""
        listing_data = {
            "title": "Short",
            "description": "Valid description that is long enough",
            "category": "escort",
            "location_country": "US",
        }

        response = client.post(
            "/api/v1/listings",
            json=listing_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_description_too_short(self, client: TestClient, auth_headers: dict) -> None:
        """Test listing with too short description."""
        listing_data = {
            "title": "Valid Title Here For Testing",
            "description": "Too short",
            "category": "escort",
            "location_country": "US",
        }

        response = client.post(
            "/api/v1/listings",
            json=listing_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_invalid_category(self, client: TestClient, auth_headers: dict) -> None:
        """Test listing with invalid category."""
        listing_data = {
            "title": "Valid Title Here For Testing",
            "description": "Valid description that is long enough to pass",
            "category": "invalid_category",
            "location_country": "US",
        }

        response = client.post(
            "/api/v1/listings",
            json=listing_data,
            headers=auth_headers,
        )

        assert response.status_code == 422