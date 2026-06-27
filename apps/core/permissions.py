"""Custom DRF permission classes usable across all apps.

Permissions can be combined by listing multiple classes in a view's
``permission_classes`` attribute.
"""

from rest_framework import permissions


class IsActiveUser(permissions.BasePermission):
    """Grant access only to authenticated users with ``is_active=True``."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)


class IsAdminUser(permissions.BasePermission):
    """Grant access only to users with ``is_staff=True`` (admin panel)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class HasGroupPermission(permissions.BasePermission):
    """Grant access only to users belonging to a specific Django group.

    Args:
        group_name: The exact name of the required Django auth group.
    """

    def __init__(self, group_name: str):
        self.group_name = group_name

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name=self.group_name).exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow read access to anyone; write access only to the object owner."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user