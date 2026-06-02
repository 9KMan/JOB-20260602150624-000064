"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""

    def test_health_check(self, client: TestClient) -> None:
        """Test basic health check endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_readiness_check(self, client: TestClient) -> None:
        """Test readiness check endpoint."""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "environment" in data
        assert "version" in data

    def test_liveness_check(self, client: TestClient) -> None:
        """Test liveness check endpoint."""
        response = client.get("/api/v1/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestWebhookEndpoints:
    """Integration tests for webhook endpoints."""

    def test_get_webhook_endpoints(self, client: TestClient) -> None:
        """Test getting webhook endpoints."""
        response = client.get("/api/v1/webhooks/providers")

        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "ccbill" in data["endpoints"]
        assert "paxum" in data["endpoints"]


class TestUserListingFlow:
    """Integration tests for user and listing workflow."""

    def test_full_user_listing_flow(
        self,
        client: TestClient,
        sample_user_data: dict,
        sample_listing_data: dict,
    ) -> None:
        """Test complete user registration to listing creation flow."""
        user_response = client.post("/api/v1/users", json=sample_user_data)
        assert user_response.status_code == 201
        user_data = user_response.json()
        user_id = user_data["id"]

        login_response = client.post(
            "/api/v1/users/login",
            json={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
        )
        assert login_response.status_code == 200
        token = login_response.json().get("token")

        headers = {"Authorization": f"Bearer {token}"}

        listing_response = client.post(
            "/api/v1/listings",
            json=sample_listing_data,
            headers=headers,
        )
        assert listing_response.status_code == 201
        listing_data = listing_response.json()
        listing_id = listing_data["id"]

        get_listing_response = client.get(f"/api/v1/listings/{listing_id}")
        assert get_listing_response.status_code == 200

        user_listings_response = client.get(f"/api/v1/listings/user/{user_id}")
        assert user_listings_response.status_code == 200
        user_listings = user_listings_response.json()
        assert len(user_listings["items"]) >= 1


class TestPaymentFlow:
    """Integration tests for payment workflow."""

    def test_payment_lifecycle(
        self,
        client: TestClient,
        test_user,
        test_listing,
        auth_headers: dict,
    ) -> None:
        """Test complete payment lifecycle."""
        payment_init_data = {
            "payment_method": "ccbill",
            "payment_type": "listing_promotion",
            "amount": "150.00",
            "currency": "USD",
            "listing_id": str(test_listing.id),
        }

        init_response = client.post(
            "/api/v1/payments/init",
            json=payment_init_data,
            headers=auth_headers,
        )
        assert init_response.status_code == 200
        payment_init = init_response.json()
        payment_id = payment_init["payment_id"]

        get_payment_response = client.get(
            f"/api/v1/payments/{payment_id}",
            headers=auth_headers,
        )
        assert get_payment_response.status_code == 200

        list_payments_response = client.get(
            "/api/v1/payments",
            headers=auth_headers,
        )
        assert list_payments_response.status_code == 200
        payments = list_payments_response.json()
        assert any(p["id"] == payment_id for p in payments["items"])


class TestSearchFunctionality:
    """Integration tests for search functionality."""

    def test_listing_search_flow(
        self,
        client: TestClient,
        test_listing: dict,
    ) -> None:
        """Test listing search flow."""
        search_response = client.get(
            "/api/v1/listings/search?"
            "query=Test&"
            "category=escort&"
            "location_country=US&"
            "sort_by=created_at&"
            "sort_order=desc&"
            "page=1&"
            "page_size=20"
        )
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert "items" in search_data
        assert "total" in search_data
        assert "page" in search_data
        assert "page_size" in search_data

    def test_search_pagination(
        self,
        client: TestClient,
        test_listing,
    ) -> None:
        """Test search pagination."""
        page1_response = client.get(
            "/api/v1/listings/search?page=1&page_size=1"
        )
        assert page1_response.status_code == 200
        page1_data = page1_response.json()

        page2_response = client.get(
            "/api/v1/listings/search?page=2&page_size=1"
        )
        assert page2_response.status_code == 200
        page2_data = page2_response.json()

        assert page1_data["total"] == page2_data["total"]
        assert page1_data["page"] == 1
        assert page2_data["page"] == 2


class TestErrorHandling:
    """Integration tests for error handling."""

    def test_invalid_uuid(self, client: TestClient) -> None:
        """Test handling of invalid UUID."""
        response = client.get("/api/v1/users/invalid-uuid")
        assert response.status_code in [404, 422]

    def test_invalid_json(self, client: TestClient) -> None:
        """Test handling of invalid JSON body."""
        response = client.post(
            "/api/v1/users",
            content=b"not valid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, client: TestClient) -> None:
        """Test handling of missing required fields."""
        response = client.post(
            "/api/v1/users",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422

    def test_cors_headers(self, client: TestClient) -> None:
        """Test CORS headers are present."""
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in response.headers or response.status_code == 200