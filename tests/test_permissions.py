import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
def test_is_admin_user_permission(api_client, user, admin_user):
    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/accounts/me/")
    assert response.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/accounts/me/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_user_inactive_cannot_login(api_client):
    User.objects.create_user(email="inactive@example.com", password="pass123", is_active=False)
    response = api_client.post("/api/v1/accounts/login/", {"email": "inactive@example.com", "password": "pass123"}, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_unauthenticated_cannot_access_protected_endpoints(api_client):
    response = api_client.get("/api/v1/accounts/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = api_client.post("/api/v1/accounts/change-password/", {}, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_change_password_requires_authentication(api_client):
    response = api_client.post("/api/v1/accounts/change-password/", {"old_password": "old", "new_password": "new"}, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED