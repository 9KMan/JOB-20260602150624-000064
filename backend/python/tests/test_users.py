"""Tests for users API."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.models.user import User, UserStatus


class TestUsersAPI:
    """Test cases for users endpoints."""

    def test_create_user_success(self, client: TestClient, sample_user_data: dict) -> None:
        """Test successful user creation."""
        response = client.post("/api/v1/users", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data

    def test_create_user_duplicate_email(
        self, client: TestClient, test_user: User, sample_user_data: dict
    ) -> None:
        """Test user creation with duplicate email."""
        sample_user_data["email"] = test_user.email

        response = client.post("/api/v1/users", json=sample_user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_create_user_invalid_password(self, client: TestClient) -> None:
        """Test user creation with weak password."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",
        }

        response = client.post("/api/v1/users", json=user_data)

        assert response.status_code == 422

    def test_get_user_by_id(self, client: TestClient, test_user: User) -> None:
        """Test getting user by ID."""
        response = client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email

    def test_get_user_not_found(self, client: TestClient) -> None:
        """Test getting non-existent user."""
        response = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404

    def test_update_user_success(
        self,
        client: TestClient,
        test_user: User,
        auth_headers: dict,
    ) -> None:
        """Test successful user update."""
        update_data = {"first_name": "Updated", "last_name": "Name"}

        response = client.patch(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"

    def test_update_user_unauthorized(self, client: TestClient, test_user: User) -> None:
        """Test updating user without authentication."""
        update_data = {"first_name": "Updated"}

        response = client.patch(f"/api/v1/users/{test_user.id}", json=update_data)

        assert response.status_code == 401

    def test_update_user_forbidden(self, client: TestClient, test_user: User) -> None:
        """Test updating another user's data."""
        update_data = {"first_name": "Hacked"}

        response = client.patch(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers={"Authorization": "Bearer wrong-token"},
        )

        assert response.status_code in [401, 403]

    def test_delete_user_success(
        self,
        client: TestClient,
        test_user: User,
        auth_headers: dict,
    ) -> None:
        """Test successful user deletion."""
        response = client.delete(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    def test_list_users(self, client: TestClient, test_user: User) -> None:
        """Test listing users."""
        response = client.get("/api/v1/users?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

    def test_list_users_with_filters(self, client: TestClient, test_user: User) -> None:
        """Test listing users with status filter."""
        response = client.get(
            f"/api/v1/users?page=1&page_size=10&status={UserStatus.ACTIVE.value}"
        )

        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == UserStatus.ACTIVE.value for item in data["items"])


class TestUserAuthentication:
    """Test cases for user authentication."""

    def test_login_success(self, client: TestClient, test_user: User) -> None:
        """Test successful login."""
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123!",
        }

        response = client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email

    def test_login_invalid_password(self, client: TestClient, test_user: User) -> None:
        """Test login with wrong password."""
        login_data = {
            "email": test_user.email,
            "password": "WrongPassword123!",
        }

        response = client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient) -> None:
        """Test login with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        }

        response = client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, client: TestClient) -> None:
        """Test email verification with invalid token."""
        verify_data = {"token": "invalid-token"}

        response = client.post("/api/v1/users/verify-email", json=verify_data)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, client: TestClient) -> None:
        """Test password reset with invalid token."""
        reset_data = {
            "token": "invalid-token",
            "new_password": "NewPassword123!",
        }

        response = client.post("/api/v1/users/reset-password", json=reset_data)

        assert response.status_code == 400