"""Structured logging middleware."""

import logging
import time
import uuid
from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.config import get_settings

settings = get_settings()


def add_request_info(
    logger: logging.Logger,
    method: str,
    path: str,
    request_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Add request information to log context."""
    return {
        "request_id": request_id,
        "method": method,
        "path": path,
    }


def configure_logging() -> None:
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.app.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""

    def __init__(self, app: Any) -> None:
        """Initialize logging middleware."""
        super().__init__(app)
        configure_logging()
        self.logger = structlog.get_logger()

    async def dispatch(self, request: Request, call_next: callable) -> Response:
        """Log request and response.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response after logging
        """
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        start_time = time.time()

        self.logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
            client_ip=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )

        try:
            response = await call_next(request)

            duration = time.time() - start_time

            self.logger.info(
                "request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )

            return response

        except Exception as e:
            duration = time.time() - start_time

            self.logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration * 1000, 2),
            )
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request.

        Args:
            request: Incoming request

        Returns:
            Client IP address
        """
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            return x_real_ip

        if request.client:
            return request.client.host

        return "unknown"