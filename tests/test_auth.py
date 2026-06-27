import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
def test_full_auth_flow(api_client, user):
    user.delete()
    register_data = {
        "email": "new@example.com",
        "password": "securepass123",
        "password_confirm": "securepass123",
    }
    response = api_client.post(
        "/api/v1/accounts/register/", register_data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED

    login_data = {"email": "new@example.com", "password": "securepass123"}
    response = api_client.post("/api/v1/accounts/login/", login_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.json()["data"]
    refresh_token = response.json()["data"]["refresh"]

    response = api_client.post(
        "/api/v1/accounts/token/refresh/", {"refresh": refresh_token}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.json()["data"]


@pytest.mark.django_db
def test_login_wrong_credentials(api_client):
    response = api_client.post(
        "/api/v1/accounts/login/",
        {"email": "fake@example.com", "password": "wrong"},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_refresh_with_invalid_token(api_client):
    response = api_client.post(
        "/api/v1/accounts/token/refresh/", {"refresh": "invalid_token"}, format="json"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
