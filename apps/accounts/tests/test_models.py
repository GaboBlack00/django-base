import pytest
from apps.accounts.models import User


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email="test@example.com", password="securepass123")
    assert user.email == "test@example.com"
    assert user.check_password("securepass123")
    assert not user.is_staff


@pytest.mark.django_db
def test_create_superuser():
    user = User.objects.create_superuser(email="admin@example.com", password="adminpass123")
    assert user.is_staff
    assert user.is_superuser


@pytest.mark.django_db
def test_email_normalized():
    user = User.objects.create_user(email="Test@EXAMPLE.COM", password="pass123")
    assert user.email == "test@example.com"


@pytest.mark.django_db
def test_create_user_without_email_raises():
    with pytest.raises(ValueError, match="Email is required"):
        User.objects.create_user(email="", password="pass123")