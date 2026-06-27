import pytest
from apps.accounts.serializers import UserRegistrationSerializer


@pytest.mark.django_db
def test_registration_serializer_valid():
    data = {
        "email": "test@example.com",
        "password": "securepass123",
        "password_confirm": "securepass123",
    }
    serializer = UserRegistrationSerializer(data=data)
    assert serializer.is_valid()


@pytest.mark.django_db
def test_registration_serializer_password_mismatch():
    data = {
        "email": "test@example.com",
        "password": "securepass123",
        "password_confirm": "differentpass",
    }
    serializer = UserRegistrationSerializer(data=data)
    assert not serializer.is_valid()
    assert "password_confirm" in serializer.errors
