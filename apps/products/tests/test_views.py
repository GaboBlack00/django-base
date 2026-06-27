import pytest
from rest_framework import status
from apps.products.models import Category, Product


# ── Product CRUD ──────────────────────────────────────────────

@pytest.mark.django_db
def test_list_products(api_client):
    response = api_client.get("/api/v1/products/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_product_authenticated(authenticated_client, user):
    category = Category.objects.create(name="Electronics")
    data = {
        "name": "Monitor",
        "description": "27 inch monitor",
        "price": "300.00",
        "category_id": category.id,
    }
    response = authenticated_client.post("/api/v1/products/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["success"] is True


@pytest.mark.django_db
def test_create_product_unauthenticated(api_client):
    data = {"name": "Test", "price": "100.00"}
    response = api_client.post("/api/v1/products/", data, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_product_negative_price(authenticated_client):
    data = {"name": "Bad", "price": "-10.00"}
    response = authenticated_client.post("/api/v1/products/", data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "price" in str(response.json()).lower()


@pytest.mark.django_db
def test_create_product_duplicate_name(authenticated_client, user_factory):
    user_factory(email="p@example.com")
    authenticated_client.post("/api/v1/products/", {"name": "Unique", "price": "10"}, format="json")
    response = authenticated_client.post("/api/v1/products/", {"name": "Unique", "price": "20"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in str(response.json()).lower()


@pytest.mark.django_db
def test_product_detail(authenticated_client, user):
    category = Category.objects.create(name="Books")
    create_resp = authenticated_client.post("/api/v1/products/", {"name": "DetailTest", "price": "15", "category_id": category.id}, format="json")
    product_id = create_resp.json()["data"]["id"]
    response = authenticated_client
    resp = response.get(f"/api/v1/products/{product_id}/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["data"]["name"] == "DetailTest"


@pytest.mark.django_db
def test_product_detail_not_found(authenticated_client):
    response = authenticated_client.get("/api/v1/products/99999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["success"] is False


@pytest.mark.django_db
def test_update_product(authenticated_client, user):
    create_resp = authenticated_client.post("/api/v1/products/", {"name": "EditMe", "price": "50"}, format="json")
    product_id = create_resp.json()["data"]["id"]
    response = authenticated_client.put(f"/api/v1/products/{product_id}/", {"name": "Edited", "price": "75"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["name"] == "Edited"
    assert response.json()["data"]["price"] == "75.00"


@pytest.mark.django_db
def test_partial_update_product(authenticated_client, user):
    create_resp = authenticated_client.post("/api/v1/products/", {"name": "PartialMe", "price": "100"}, format="json")
    product_id = create_resp.json()["data"]["id"]
    response = authenticated_client.patch(f"/api/v1/products/{product_id}/", {"name": "PartiallyUpdated"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["name"] == "PartiallyUpdated"
    assert response.json()["data"]["price"] == "100.00"


@pytest.mark.django_db
def test_delete_product(authenticated_client, user):
    create_resp = authenticated_client.post("/api/v1/products/", {"name": "DeleteMe", "price": "30"}, format="json")
    product_id = create_resp.json()["data"]["id"]
    response = authenticated_client.delete(f"/api/v1/products/{product_id}/")
    assert response.status_code == status.HTTP_200_OK
    assert Product.objects.filter(pk=product_id).exists() is False


@pytest.mark.django_db
def test_update_product_by_non_owner(api_client, user, user_factory):
    other_user = user_factory(email="other@example.com")
    api_client.force_authenticate(user=other_user)
    product = Product.objects.create(name="Owned", price=10, created_by=user)
    response = api_client.put(f"/api/v1/products/{product.pk}/", {"name": "Hacked", "price": "99"}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ── Category CRUD ─────────────────────────────────────────────

@pytest.mark.django_db
def test_list_categories(api_client):
    Category.objects.create(name="Electronics")
    response = api_client.get("/api/v1/products/categories/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_category_as_staff(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post("/api/v1/products/categories/", {"name": "StaffCategory"}, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["name"] == "StaffCategory"


@pytest.mark.django_db
def test_create_category_as_non_staff(api_client, user):
    api_client.force_authenticate(user=user)
    response = api_client.post("/api/v1/products/categories/", {"name": "NoPerm"}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_category_detail(api_client):
    cat = Category.objects.create(name="DetailCat")
    response = api_client.get(f"/api/v1/products/categories/{cat.pk}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["name"] == "DetailCat"


@pytest.mark.django_db
def test_category_detail_not_found(api_client):
    response = api_client.get("/api/v1/products/categories/99999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_category_as_staff(api_client, admin_user):
    cat = Category.objects.create(name="OldName")
    api_client.force_authenticate(user=admin_user)
    response = api_client.put(f"/api/v1/products/categories/{cat.pk}/", {"name": "NewName"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert Category.objects.get(pk=cat.pk).name == "NewName"


@pytest.mark.django_db
def test_delete_category_as_staff(api_client, admin_user):
    cat = Category.objects.create(name="DeleteCat")
    api_client.force_authenticate(user=admin_user)
    response = api_client.delete(f"/api/v1/products/categories/{cat.pk}/")
    assert response.status_code == status.HTTP_200_OK
    assert Category.objects.filter(pk=cat.pk).exists() is False


@pytest.mark.django_db
def test_delete_category_as_non_staff(api_client, user):
    cat = Category.objects.create(name="NoDelete")
    api_client.force_authenticate(user=user)
    response = api_client.delete(f"/api/v1/products/categories/{cat.pk}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ── Filters, Search & Ordering ───────────────────────────────

@pytest.mark.django_db
def test_filter_products_by_category(authenticated_client, user):
    cat_a = Category.objects.create(name="A")
    cat_b = Category.objects.create(name="B")
    authenticated_client.post("/api/v1/products/", {"name": "ProdA", "price": "10", "category_id": cat_a.id}, format="json")
    authenticated_client.post("/api/v1/products/", {"name": "ProdB", "price": "20", "category_id": cat_b.id}, format="json")
    response = authenticated_client.get(f"/api/v1/products/?category={cat_a.id}")
    names = [p["name"] for p in response.json()["data"]]
    assert "ProdA" in names
    assert "ProdB" not in names


@pytest.mark.django_db
def test_search_products(authenticated_client, user):
    authenticated_client.post("/api/v1/products/", {"name": "Laptop Pro", "price": "1500"}, format="json")
    authenticated_client.post("/api/v1/products/", {"name": "Mouse Pad", "price": "20"}, format="json")
    response = authenticated_client.get("/api/v1/products/?search=Laptop")
    names = [p["name"] for p in response.json()["data"]]
    assert "Laptop Pro" in names
    assert "Mouse Pad" not in names


@pytest.mark.django_db
def test_order_products_by_price(authenticated_client, user):
    authenticated_client.post("/api/v1/products/", {"name": "Cheap", "price": "5"}, format="json")
    authenticated_client.post("/api/v1/products/", {"name": "Expensive", "price": "100"}, format="json")
    response = authenticated_client.get("/api/v1/products/?ordering=price")
    data = response.json()["data"]
    assert data[0]["price"] == "5.00"
    assert data[-1]["price"] == "100.00"