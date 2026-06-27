"""Read-only queries for products and categories.

Separated from services to follow a lightweight CQRS pattern.
Queries use ``select_related`` to avoid N+1 queries on FK relationships.
"""

from django.db import models
from django.db.models import QuerySet
from .models import Category, Product


def get_categories() -> QuerySet:
    """Return all categories."""
    return Category.objects.all()


def get_category_by_id(category_id: int) -> Category | None:
    """Look up a category by its primary key.

    Args:
        category_id: The category's ID.

    Returns:
        The matching ``Category`` instance, or ``None``.
    """
    return Category.objects.filter(id=category_id).first()


def get_products(
    category_id: int | None = None,
    is_active: bool | None = None,
    search: str | None = None,
) -> QuerySet:
    """Return filtered products with optimised FK joins.

    Args:
        category_id: Filter by category primary key (optional).
        is_active: Filter by active status (optional).
        search: Text search against ``name`` and ``description`` (optional).

    Returns:
        A ``QuerySet`` of ``Product`` instances with ``select_related``.
    """
    qs = Product.objects.select_related("category", "created_by")

    if category_id is not None:
        qs = qs.filter(category_id=category_id)

    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    if search:
        qs = qs.filter(
            models.Q(name__icontains=search) | models.Q(description__icontains=search)
        )

    return qs


def get_product_by_id(product_id: int) -> Product | None:
    """Look up a product by its primary key with related data.

    Args:
        product_id: The product's ID.

    Returns:
        The matching ``Product`` instance with ``category`` and
        ``created_by`` prefetched, or ``None``.
    """
    return Product.objects.select_related("category", "created_by").filter(
        id=product_id
    ).first()
