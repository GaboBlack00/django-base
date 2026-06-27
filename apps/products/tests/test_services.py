import pytest
from django.core.exceptions import ValidationError
from apps.products.services import ProductService, CategoryService


@pytest.mark.django_db
def test_create_product_service(user):
    product = ProductService.create_product(
        name="Keyboard",
        price=100.00,
        description="Mechanical keyboard",
        created_by=user,
    )
    assert product.name == "Keyboard"
    assert product.price == 100.00


@pytest.mark.django_db
def test_create_product_negative_price(user):
    with pytest.raises(ValidationError, match="Price must be greater than 0"):
        ProductService.create_product(name="Test", price=-10, created_by=user)


@pytest.mark.django_db
def test_create_category_service():
    category = CategoryService.create_category(name="Books", description="All kinds of books")
    assert category.name == "Books"