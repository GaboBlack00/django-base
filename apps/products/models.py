"""Product and Category domain models for the e-commerce module.
"""

from django.conf import settings
from django.db import models


class Category(models.Model):
    """Product category with a computed count of active products."""

    name = models.CharField("name", max_length=100, unique=True)
    description = models.TextField("description", blank=True)
    created_at = models.DateTimeField("created", auto_now_add=True)
    updated_at = models.DateTimeField("updated", auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def product_count(self) -> int:
        """Return the number of active products in this category."""
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """Individual product linked to a category and a creator user."""

    name = models.CharField("name", max_length=200, unique=True)
    description = models.TextField("description", blank=True)
    price = models.DecimalField(
        "price", max_digits=10, decimal_places=2,
        help_text="Price must be greater than 0. Example: 19.99",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    is_active = models.BooleanField("active", default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
    )
    created_at = models.DateTimeField("created", auto_now_add=True)
    updated_at = models.DateTimeField("updated", auto_now=True)

    class Meta:
        db_table = "products"
        verbose_name = "product"
        verbose_name_plural = "products"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
