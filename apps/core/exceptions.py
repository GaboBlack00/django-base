"""Custom exception classes and global exception handler.

Provides structured error responses consistent across the API.
All DRF exceptions are intercepted and wrapped in ``{success, error}`` format.
"""

import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response

logger = logging.getLogger("api")


class ServiceException(APIException):
    """Base exception for service-layer errors.

    Attributes:
        status_code: HTTP 400 Bad Request.
        default_detail: Human-readable default message.
        default_code: Machine-readable error code.
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail: str = "Service error"
    default_code: str = "SERVICE_ERROR"


class PermissionDeniedService(ServiceException):
    """Raised when a service-level permission check fails.

    Attributes:
        status_code: HTTP 403 Forbidden.
        default_code: ``PERMISSION_DENIED``.
    """

    status_code: int = status.HTTP_403_FORBIDDEN
    default_detail: str = "Permission denied"
    default_code: str = "PERMISSION_DENIED"


class ConflictError(ServiceException):
    """Raised when a resource conflict occurs (e.g. duplicate email).

    Attributes:
        status_code: HTTP 409 Conflict.
        default_code: ``CONFLICT``.
    """

    status_code: int = status.HTTP_409_CONFLICT
    default_detail: str = "Resource conflict"
    default_code: str = "CONFLICT"


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """Wrap DRF exceptions into a unified ``{success, error}`` response.

    Args:
        exc: The exception instance (DRF ``APIException`` or custom subclass).
        context: DRF exception context dict containing the view and request.

    Returns:
        A ``Response`` object with the unified error format, or ``None`` if
        the exception is not handled by DRF.
    """
    response = drf_exception_handler(exc, context)

    if response is not None:
        code: str = getattr(exc, "default_code", "ERROR")
        detail = exc.detail if hasattr(exc, "detail") else str(exc)

        if isinstance(detail, dict):
            error_detail = detail
        elif isinstance(detail, list):
            error_detail = {"messages": detail}
        else:
            error_detail = {"message": str(detail)}

        response.data = {
            "success": False,
            "error": {
                "code": code,
                "detail": error_detail,
            },
        }

        logger.warning(
            "API Exception: %s - %s",
            code,
            error_detail,
            extra={"request_id": getattr(context.get("request"), "id", None)},
        )

    return response
