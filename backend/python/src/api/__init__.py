"""API package."""

from fastapi import APIRouter

from src.api.v1 import users, listings, payments, webhooks, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(listings.router, prefix="/listings", tags=["Listings"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])