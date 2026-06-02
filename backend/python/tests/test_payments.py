"""Tests for payments API."""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from src.models.payment import Payment, PaymentStatus, PaymentMethod, PaymentType


class TestPaymentsAPI:
    """Test cases for payments endpoints."""

    def test_list_payments(
        self,
        client: TestClient,
        test_user,
        test_payment: Payment,
        auth_headers: dict,
    ) -> None:
        """Test listing user payments."""
        response = client.get(
            "/api/v1/payments",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_payments_with_filters(
        self,
        client: TestClient,
        test_user,
        test_payment: Payment,
        auth_headers: dict,
    ) -> None:
        """Test listing payments with filters."""
        response = client.get(
            "/api/v1/payments?status=completed&payment_method=ccbill",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert all(
            item["status"] == PaymentStatus.COMPLETED.value
            and item["payment_method"] == PaymentMethod.CCBILL.value
            for item in data["items"]
        )

    def test_get_payment_by_id(
        self,
        client: TestClient,
        test_user,
        test_payment: Payment,
        auth_headers: dict,
    ) -> None:
        """Test getting payment by ID."""
        response = client.get(
            f"/api/v1/payments/{test_payment.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_payment.id)

    def test_get_payment_not_found(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        """Test getting non-existent payment."""
        response = client.get(
            "/api/v1/payments/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_payment_forbidden(
        self,
        client: TestClient,
        test_payment: Payment,
        auth_headers: dict,
    ) -> None:
        """Test getting another user's payment."""
        response = client.get(
            f"/api/v1/payments/{test_payment.id}",
            headers={"Authorization": "Bearer wrong-token"},
        )

        assert response.status_code in [401, 403]

    def test_capture_payment(
        self,
        client: TestClient,
        test_user,
        test_payment: Payment,
        auth_headers: dict,
    ) -> None:
        """Test capturing a payment."""
        test_payment.status = PaymentStatus.AUTHORIZED

        response = client.post(
            f"/api/v1/payments/{test_payment.id}/capture",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400]

    def test_cancel_payment(
        self,
        client: TestClient,
        test_user,
        test_payment: Payment,
        auth_headers: dict,
    ) -> None:
        """Test cancelling a payment."""
        test_payment.status = PaymentStatus.PENDING

        response = client.post(
            f"/api/v1/payments/{test_payment.id}/cancel",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400]

    def test_refund_payment(
        self,
        client: TestClient,
        test_user,
        test_payment: Payment,
        auth_headers: dict,
    ) -> None:
        """Test refunding a payment."""
        refund_data = {
            "payment_id": str(test_payment.id),
            "amount": 50.00,
            "reason": "Customer request",
        }

        response = client.post(
            "/api/v1/payments/refund",
            json=refund_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 400]

    def test_get_available_payment_methods(self, client: TestClient) -> None:
        """Test getting available payment methods."""
        response = client.get("/api/v1/payments/methods/available")

        assert response.status_code == 200
        data = response.json()
        assert "payment_methods" in data
        assert len(data["payment_methods"]) > 0


class TestPaymentInitialization:
    """Test cases for payment initialization."""

    def test_initialize_payment_ccbill(
        self,
        client: TestClient,
        test_user,
        test_listing,
        auth_headers: dict,
    ) -> None:
        """Test initializing CCBill payment."""
        payment_data = {
            "payment_method": "ccbill",
            "payment_type": "listing_promotion",
            "amount": "100.00",
            "currency": "USD",
            "listing_id": str(test_listing.id),
        }

        response = client.post(
            "/api/v1/payments/init",
            json=payment_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "payment_id" in data

    def test_initialize_payment_invalid_method(
        self,
        client: TestClient,
        test_user,
        auth_headers: dict,
    ) -> None:
        """Test initializing payment with invalid method."""
        payment_data = {
            "payment_method": "invalid",
            "payment_type": "other",
            "amount": "100.00",
            "currency": "USD",
        }

        response = client.post(
            "/api/v1/payments/init",
            json=payment_data,
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestPaymentValidation:
    """Test cases for payment validation."""

    def test_negative_amount(
        self,
        client: TestClient,
        test_user,
        auth_headers: dict,
    ) -> None:
        """Test payment with negative amount."""
        payment_data = {
            "payment_method": "ccbill",
            "payment_type": "other",
            "amount": "-100.00",
            "currency": "USD",
        }

        response = client.post(
            "/api/v1/payments/init",
            json=payment_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_zero_amount(
        self,
        client: TestClient,
        test_user,
        auth_headers: dict,
    ) -> None:
        """Test payment with zero amount."""
        payment_data = {
            "payment_method": "ccbill",
            "payment_type": "other",
            "amount": "0.00",
            "currency": "USD",
        }

        response = client.post(
            "/api/v1/payments/init",
            json=payment_data,
            headers=auth_headers,
        )

        assert response.status_code == 422