"""DRF view mixins for consistent API response formatting.

Reusable across any ``RetrieveUpdateDestroyAPIView`` or
``RetrieveUpdateAPIView`` that should wrap responses in the
``api_response()`` envelope.
"""

from rest_framework import status
from rest_framework.response import Response

from apps.core.response import api_response


class APIResponseMixin:
    """Mixin that wraps update, partial_update, and destroy in ``api_response()``.

    Overrides the default DRF behaviour so every mutating endpoint returns
    a consistent ``{success, data}`` envelope instead of raw serializer output.

    Class Attributes:
        destroy_message: Human-readable string returned on successful DELETE.
    """

    destroy_message: str = "Resource deleted"

    def update(self, request, *args, **kwargs) -> Response:
        """Full or partial update with ``api_response`` wrapping."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return api_response(success=True, data=self.get_serializer(instance).data)

    def partial_update(self, request, *args, **kwargs) -> Response:
        """Delegate to ``update`` with ``partial=True``."""
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs) -> Response:
        """Delete the resource and return a 200 with a confirmation message."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return api_response(
            success=True,
            data={"message": self.destroy_message},
            status_code=status.HTTP_200_OK,
        )
