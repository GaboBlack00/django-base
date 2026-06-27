import pytest
from rest_framework.exceptions import ValidationError
from apps.accounts.models import User
from apps.accounts.services import UserService


@pytest.mark.django_db
def test_create_user_service():
    user = UserService.create_user(
        email="test@example.com", password="securepass123", first_name="John"
    )
    assert user.email == "test@example.com"
    assert user.first_name == "John"


@pytest.mark.django_db
def test_create_user_duplicate_email():
    User.objects.create_user(email="test@example.com", password="pass123")
    with pytest.raises(ValidationError, match="This email is already registered"):
        UserService.create_user(email="test@example.com", password="pass123")


@pytest.mark.django_db
def test_change_password():
    user = User.objects.create_user(email="test@example.com", password="oldpass123")
    UserService.change_password(user, "oldpass123", "newpass456")
    assert user.check_password("newpass456")


@pytest.mark.django_db
def test_change_password_wrong_old():
    user = User.objects.create_user(email="test@example.com", password="oldpass123")
    with pytest.raises(ValidationError, match="Current password is incorrect"):
        UserService.change_password(user, "wrongpass", "newpass456")
