"""Custom DRF permissions for the products module.
"""

from rest_framework import permissions


class IsProductOwnerOrReadOnly(permissions.BasePermission):
    """Allow read access to anyone; write access only to the creator or staff."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True

        return obj.created_by == request.user


class IsStaffForCategories(permissions.BasePermission):
    """Allow read access to anyone; write access restricted to staff users."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff
