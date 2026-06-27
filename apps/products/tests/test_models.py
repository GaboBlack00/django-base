import pytest
from apps.accounts.models import User
from apps.products.models import Category, Product


@pytest.mark.django_db
def test_create_category():
    category = Category.objects.create(name="Electronics", description="Electronic items")
    assert category.name == "Electronics"
    assert category.product_count == 0


@pytest.mark.django_db
def test_create_product(user):
    category = Category.objects.create(name="Electronics")
    product = Product.objects.create(
        name="Laptop",
        description="Gaming laptop",
        price=1500.00,
        category=category,
        created_by=user,
    )
    assert product.name == "Laptop"
    assert product.price == 1500.00
    assert product.category == category
    assert product.is_active is True


@pytest.mark.django_db
def test_product_str():
    category = Category.objects.create(name="Electronics")
    user = User.objects.create_user(email="test@example.com", password="pass123")
    product = Product.objects.create(name="Mouse", price=25.00, category=category, created_by=user)
    assert str(product) == "Mouse"