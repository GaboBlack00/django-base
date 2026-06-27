"""Business logic for product and category CRUD operations.

Encapsulates validation, uniqueness checks, and persistence so views
and serializers only handle HTTP and serialisation concerns.
"""

from rest_framework.exceptions import ValidationError
from django.db import transaction
from .models import Category, Product


class ProductService:
    """Stateless service for creating, updating, and deleting products."""

    @staticmethod
    @transaction.atomic
    def create_product(
        name: str,
        price: float,
        description: str = "",
        category=None,
        created_by=None,
    ):
        """Create a new product after validating price and name uniqueness.

        Args:
            name: Product name (case-insensitive unique).
            price: Must be greater than zero.
            description: Optional description.
            category: Optional ``Category`` instance.
            created_by: The ``User`` who created the product.

        Returns:
            The newly created ``Product`` instance.

        Raises:
            ValidationError: If price is <= 0 or the name already exists.
        """
        if price <= 0:
            raise ValidationError({"price": "Price must be greater than 0"})

        if Product.objects.filter(name__iexact=name).exists():
            raise ValidationError({"name": "A product with this name already exists"})

        return Product.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def update_product(product, **kwargs):
        """Update product fields after validating price (if provided).

        Args:
            product: The ``Product`` instance to update.
            **kwargs: Fields to update (e.g. ``name``, ``price``, ``description``).

        Returns:
            The updated ``Product`` instance.

        Raises:
            ValidationError: If the provided price is <= 0.
        """
        if "price" in kwargs and kwargs["price"] <= 0:
            raise ValidationError({"price": "Price must be greater than 0"})

        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)

        product.full_clean()
        product.save()
        return product

    @staticmethod
    def delete_product(product):
        """Delete a product instance.

        Args:
            product: The ``Product`` instance to delete.
        """
        product.delete()


class CategoryService:
    """Stateless service for creating and updating categories."""

    @staticmethod
    @transaction.atomic
    def create_category(name: str, description: str = ""):
        """Create a new category after validating name uniqueness.

        Args:
            name: Category name (case-insensitive unique).
            description: Optional description.

        Returns:
            The newly created ``Category`` instance.

        Raises:
            ValidationError: If the name already exists.
        """
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError({"name": "A category with this name already exists"})

        return Category.objects.create(name=name, description=description)

    @staticmethod
    @transaction.atomic
    def update_category(category, **kwargs):
        """Update category fields.

        Args:
            category: The ``Category`` instance to update.
            **kwargs: Fields to update (e.g. ``name``, ``description``).

        Returns:
            The updated ``Category`` instance.
        """
        for key, value in kwargs.items():
            if hasattr(category, key):
                setattr(category, key, value)

        category.full_clean()
        category.save()
        return category
