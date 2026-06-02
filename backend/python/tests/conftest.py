"""Pytest configuration and fixtures."""

import os
import uuid
from datetime import datetime, timezone
from typing import Generator
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["AUTH0_DOMAIN"] = ""
os.environ["AUTH0_AUDIENCE"] = ""

from src.database import Base, get_db
from src.main import app
from src.models.user import User, UserStatus, UserVerificationStatus
from src.models.listing import Listing, ListingStatus, ListingCategory
from src.models.payment import Payment, PaymentStatus, PaymentMethod, PaymentType
from src.utils.security import get_password_hash


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPassword123!"),
        first_name="Test",
        last_name="User",
        status=UserStatus.ACTIVE,
        verification_status=UserVerificationStatus.VERIFIED,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_unverified(db_session) -> User:
    """Create an unverified test user."""
    user = User(
        id=uuid.uuid4(),
        email="unverified@example.com",
        username="unverifieduser",
        hashed_password=get_password_hash("TestPassword123!"),
        status=UserStatus.PENDING,
        verification_status=UserVerificationStatus.UNVERIFIED,
        is_email_verified=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_listing(db_session, test_user) -> Listing:
    """Create a test listing."""
    listing = Listing(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Test Listing Title Here",
        slug="test-listing-title-here-abc12345",
        description="This is a test listing description that is long enough to pass validation.",
        short_description="A short test description",
        category=ListingCategory.ESCORT,
        status=ListingStatus.ACTIVE,
        location_country="US",
        location_city="New York",
        price_amount=100.00,
        price_currency="USD",
    )
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)
    return listing


@pytest.fixture
def test_payment(db_session, test_user, test_listing) -> Payment:
    """Create a test payment."""
    payment = Payment(
        id=uuid.uuid4(),
        user_id=test_user.id,
        listing_id=test_listing.id,
        status=PaymentStatus.COMPLETED,
        payment_method=PaymentMethod.CCBILL,
        payment_type=PaymentType.LISTING_PROMOTION,
        amount=100.00,
        currency="USD",
        provider_reference="ccbill_test_123",
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    return payment


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    mock.lpush.return_value = 1
    mock.rpop.return_value = None
    mock.ttl.return_value = -1
    return mock


@pytest.fixture
def auth_headers(test_user) -> dict:
    """Create authentication headers for test user."""
    from src.utils.security import create_access_token

    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_listing_data() -> dict:
    """Sample listing data for tests."""
    return {
        "title": "Premium Service Listing",
        "description": "This is a premium service listing with all the details needed for testing purposes.",
        "short_description": "Premium service",
        "category": "escort",
        "price_amount": 150.00,
        "price_currency": "USD",
        "location_country": "US",
        "location_city": "Los Angeles",
        "location_state": "CA",
    }


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for tests."""
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "NewUserPassword123!",
        "first_name": "New",
        "last_name": "User",
    }