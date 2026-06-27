"""Custom Django middleware for request tracing, IP whitelisting, and logging.

Middlewares are registered in ``MIDDLEWARE`` in ``config/settings/base.py``.
"""

import logging
import time
import uuid

from django.conf import settings
from django.http import HttpRequest, JsonResponse

logger = logging.getLogger("api")


class RequestIDMiddleware:
    """Assign a unique UUID to every request and expose it via ``X-Request-ID``.

    The ID is available as ``request.id`` throughout the request-response cycle
    and is included in API logs for traceability.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request.id = str(uuid.uuid4())
        response = self.get_response(request)
        response["X-Request-ID"] = request.id
        return response


class IPWhitelistAdminMiddleware:
    """Restrict ``/admin/`` access to configured IP addresses in production.

    Reads ``ADMIN_IP_WHITELIST`` from Django settings. If the list is non-empty
    and the request targets ``/admin/``, the client IP must be present.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        admin_ip_whitelist = getattr(settings, "ADMIN_IP_WHITELIST", [])
        if admin_ip_whitelist and request.path.startswith("/admin/"):
            client_ip = self._get_client_ip(request)
            if client_ip not in admin_ip_whitelist:
                return JsonResponse(
                    {
                        "success": False,
                        "error": {"code": "FORBIDDEN", "detail": "Access denied"},
                    },
                    status=403,
                )
        return self.get_response(request)

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract the real client IP, respecting ``X-Forwarded-For``.

        Args:
            request: The Django HTTP request.

        Returns:
            The client IP address as a string.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")


class APILoggingMiddleware:
    """Log every API request with method, path, status, duration, and user.

    Logs are written at ``INFO`` level to the ``api`` logger with the
    ``request_id`` from ``RequestIDMiddleware`` for traceability.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        logger.info(
            "API Request: %s %s - %s - %.3fs - user=%s",
            request.method,
            request.path,
            response.status_code,
            duration,
            getattr(request.user, "email", "anonymous"),
            extra={"request_id": getattr(request, "id", None)},
        )

        return response
