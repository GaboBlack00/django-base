"""Django-filter ``FilterSet`` definitions for the products module.
"""

import django_filters
from django.db import models
from django.db.models import QuerySet
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """Filter products by category, active status, and free-text search.

    The ``search`` field is a custom CharFilter that matches against
    both ``name`` and ``description``.
    """

    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Product
        fields = ["category", "is_active"]

    def filter_search(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        """Apply a case-insensitive search across ``name`` and ``description``.

        Args:
            queryset: The current queryset to filter.
            name: The field name (``search``).
            value: The search term.

        Returns:
            The filtered ``QuerySet``.
        """
        return queryset.filter(
            models.Q(name__icontains=value) | models.Q(description__icontains=value)
        )
