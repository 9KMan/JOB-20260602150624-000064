"""Health check API router."""

from datetime import datetime, timezone

from fastapi import APIRouter, status

from src.config import get_settings

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> dict:
    """Readiness check endpoint."""
    settings = get_settings()
    return {
        "status": "ready",
        "environment": settings.app.environment,
        "version": settings.app.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> dict:
    """Liveness check endpoint."""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }