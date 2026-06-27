"""DRF serializers for products and categories.

Includes separate serializers for list (lightweight) and detail (full)
representations, plus a dedicated create/update serializer with
price and name validations.
"""

from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Category representation including the count of active products."""

    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "description", "product_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight product representation for list views.

    Includes the category name as a flat string rather than a nested object.
    """

    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "price", "category", "category_name", "is_active"]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product representation for detail views and creation.

    Accepts ``category_id`` on write (just the PK) and returns the full
    nested ``CategorySerializer`` on read.
    """

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
        help_text="ID of an existing category. Use GET /api/v1/products/categories/ to list them.",
    )
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "category_id",
            "is_active",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_email", "created_at", "updated_at"]

    def validate_price(self, value):
        """Ensure price is a positive value."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_name(self, value):
        """Ensure product name is unique (case-insensitive)."""
        pk = self.instance.pk if self.instance else None
        if Product.objects.filter(name__iexact=value).exclude(pk=pk).exists():
            raise serializers.ValidationError("A product with this name already exists")
        return value

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
