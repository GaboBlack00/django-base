"""Unified API response helper.

All views should use ``api_response()`` to maintain a consistent
``{success, data}`` / ``{success, error}`` format across the API.
"""

from rest_framework.response import Response


def api_response(
    success: bool = True, data=None, error=None, status_code: int = 200
) -> Response:
    """Build a standardised JSON response.

    Args:
        success: Whether the request succeeded.
        data: Payload for successful responses (optional).
        error: Error detail for failed responses (optional).
        status_code: HTTP status code (default 200).

    Returns:
        A DRF ``Response`` with the unified envelope.
    """
    if success:
        return Response({"success": True, "data": data}, status=status_code)
    return Response({"success": False, "error": error}, status=status_code)
