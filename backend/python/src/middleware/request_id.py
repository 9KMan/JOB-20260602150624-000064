"""Request ID middleware for request tracing."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to each request."""

    HEADER_NAME = "X-Request-ID"

    async def dispatch(self, request: Request, call_next: callable) -> Response:
        """Process request and add request ID header.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with request ID header
        """
        request_id = request.headers.get(self.HEADER_NAME)

        if not request_id:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers[self.HEADER_NAME] = request_id

        return response