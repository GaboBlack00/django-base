import pytest
from apps.products.models import Category
from apps.products.serializers import CategorySerializer


@pytest.mark.django_db
def test_category_serializer():
    category = Category.objects.create(name="Electronics")
    serializer = CategorySerializer(category)
    assert serializer.data["name"] == "Electronics"
