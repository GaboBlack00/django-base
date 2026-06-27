import pytest
from rest_framework import status
from apps.accounts.models import User


@pytest.mark.django_db
def test_register_view(api_client):
    data = {
        "email": "test@example.com",
        "password": "securepass123",
        "password_confirm": "securepass123",
    }
    response = api_client.post("/api/v1/accounts/register/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["success"] is True


@pytest.mark.django_db
def test_register_duplicate_email(api_client):
    User.objects.create_user(email="dup@example.com", password="pass123")
    data = {
        "email": "dup@example.com",
        "password": "TestPass123",
        "password_confirm": "TestPass123",
    }
    response = api_client.post("/api/v1/accounts/register/", data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["success"] is False


@pytest.mark.django_db
def test_register_password_mismatch(api_client):
    data = {
        "email": "test@example.com",
        "password": "pass123",
        "password_confirm": "different",
    }
    response = api_client.post("/api/v1/accounts/register/", data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["success"] is False


@pytest.mark.django_db
def test_login_view(api_client):
    User.objects.create_user(email="test@example.com", password="securepass123")
    data = {"email": "test@example.com", "password": "securepass123"}
    response = api_client.post("/api/v1/accounts/login/", data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True
    assert "access" in response.json()["data"]
    assert "refresh" in response.json()["data"]


@pytest.mark.django_db
def test_profile_view_requires_auth(api_client):
    response = api_client.get("/api/v1/accounts/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_profile_view_authenticated(api_client):
    user = User.objects.create_user(email="test@example.com", password="securepass123")
    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/accounts/me/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["email"] == "test@example.com"


@pytest.mark.django_db
def test_profile_update(api_client):
    user = User.objects.create_user(
        email="update@example.com", password="securepass123"
    )
    api_client.force_authenticate(user=user)
    response = api_client.patch(
        "/api/v1/accounts/me/", {"first_name": "John"}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["first_name"] == "John"


@pytest.mark.django_db
def test_change_password_happy_path(api_client):
    user = User.objects.create_user(email="changeme@example.com", password="oldpass123")
    api_client.force_authenticate(user=user)
    response = api_client.post(
        "/api/v1/accounts/change-password/",
        {"old_password": "oldpass123", "new_password": "Newpass123!"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True
    user.refresh_from_db()
    assert user.check_password("Newpass123!")


@pytest.mark.django_db
def test_change_password_wrong_old(api_client):
    user = User.objects.create_user(email="wrongme@example.com", password="oldpass123")
    api_client.force_authenticate(user=user)
    response = api_client.post(
        "/api/v1/accounts/change-password/",
        {"old_password": "wrongpass", "new_password": "Newpass123!"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
