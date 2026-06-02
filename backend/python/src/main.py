"""FastAPI main application."""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge

from src.config import get_settings
from src.api import api_router
from src.middleware.request_id import RequestIDMiddleware
from src.middleware.logging import LoggingMiddleware
from src.database import db_manager

logger = logging.getLogger(__name__)
settings = get_settings()

request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
)

active_requests = Gauge(
    "http_requests_active",
    "Number of active HTTP requests",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan handler."""
    logger.info("Starting Premium Service Directory API")

    db_manager.init()
    logger.info("Database connection pool initialized")

    yield

    logger.info("Shutting down Premium Service Directory API")
    db_manager.engine.dispose()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app.app_name,
        version=settings.app.app_version,
        description="Premium Service Directory Platform API",
        docs_url="/docs" if settings.app.environment == "development" else None,
        redoc_url="/redoc" if settings.app.environment == "development" else None,
        openapi_url="/openapi.json" if settings.app.environment != "production" else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    app.include_router(api_router, prefix="/api/v1")

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler for unhandled errors."""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            f"Unhandled exception: {exc}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handler for ValueError exceptions."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation error",
                "message": str(exc),
            },
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app.debug,
        log_level=settings.app.log_level.lower(),
    )