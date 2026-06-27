"""Django admin configuration for products and categories.
"""

from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for managing product categories."""

    list_display = ["name", "product_count", "created_at"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for managing products with inline creator assignment."""

    list_display = ["name", "price", "category", "is_active", "created_by", "created_at"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "description"]
    ordering = ["-created_at"]
    readonly_fields = ["created_by", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        obj.save()
