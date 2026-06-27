"""Business logic for user-related operations.

Encapsulates validation and persistence rules so that views and serializers
remain thin and logic is reusable across different entry points.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserService:
    """Stateless service for user creation and password management."""

    @staticmethod
    def create_user(
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        **extra_fields,
    ):
        """Create a new user after validating email uniqueness and password strength.

        Args:
            email: User's email address (case-insensitive, stored lowercased).
            password: Plain-text password (validated against Django rules).
            first_name: Optional first name.
            last_name: Optional last name.
            **extra_fields: Additional fields passed to ``User.objects.create_user()``.

        Returns:
            The newly created ``User`` instance.

        Raises:
            ValidationError: If the email is already registered or password
                does not meet strength requirements.
        """
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError({"email": "This email is already registered"})
        validate_password(password)
        return User.objects.create_user(
            email=email.lower(),
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )

    @staticmethod
    def change_password(user, old_password: str, new_password: str):
        """Change a user's password after verifying the current one.

        Args:
            user: The ``User`` instance whose password will be changed.
            old_password: Current password for verification.
            new_password: New password (validated against Django rules).

        Raises:
            ValidationError: If ``old_password`` is incorrect or the new
                password is too weak.
        """
        if not user.check_password(old_password):
            raise ValidationError({"old_password": "Current password is incorrect"})
        validate_password(new_password)
        user.set_password(new_password)
        user.save()
