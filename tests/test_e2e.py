import pytest
from rest_framework import status


@pytest.mark.django_db
class TestE2EFlow:
    def test_full_user_journey(self, api_client):
        # 1. Register
        register_data = {
            "email": "e2e@example.com",
            "password": "StrongPass1!",
            "password_confirm": "StrongPass1!",
        }
        resp = api_client.post(
            "/api/v1/accounts/register/", register_data, format="json"
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["success"] is True

        # 2. Login
        login_data = {"email": "e2e@example.com", "password": "StrongPass1!"}
        resp = api_client.post("/api/v1/accounts/login/", login_data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["success"] is True
        access_token = resp.json()["data"]["access"]
        refresh_token = resp.json()["data"]["refresh"]

        # 3. Access /me/ with token
        resp = api_client.get(
            "/api/v1/accounts/me/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["data"]["email"] == "e2e@example.com"

        # 4. Refresh token
        resp = api_client.post(
            "/api/v1/accounts/token/refresh/", {"refresh": refresh_token}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK
        assert "access" in resp.json()["data"]

        # 5. Update profile
        resp = api_client.patch(
            "/api/v1/accounts/me/",
            {"first_name": "E2E"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["data"]["first_name"] == "E2E"

        # 6. Create a product
        resp = api_client.post(
            "/api/v1/products/",
            {"name": "E2E Product", "price": "99.99"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        product_id = resp.json()["data"]["id"]

        # 7. List products
        resp = api_client.get(
            "/api/v1/products/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        assert resp.status_code == status.HTTP_200_OK
        ids = [p["id"] for p in resp.json()["data"]]
        assert product_id in ids

        # 8. Update product
        resp = api_client.put(
            f"/api/v1/products/{product_id}/",
            {"name": "E2E Updated", "price": "49.99"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["data"]["name"] == "E2E Updated"

        # 9. Delete product
        resp = api_client.delete(
            f"/api/v1/products/{product_id}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        assert resp.status_code == status.HTTP_200_OK

        # 10. Change password
        resp = api_client.post(
            "/api/v1/accounts/change-password/",
            {"old_password": "StrongPass1!", "new_password": "NewPass123!"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["success"] is True

        # 11. Login with new password
        resp = api_client.post(
            "/api/v1/accounts/login/",
            {"email": "e2e@example.com", "password": "NewPass123!"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["success"] is True
