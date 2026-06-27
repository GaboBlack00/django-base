"""Read-only queries for the ``User`` model.

Separates lookup logic from business logic (services) to follow a
lightweight CQRS pattern.
"""

from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_email(email: str):
    """Look up a user by email (case-insensitive).

    Args:
        email: The email address to search for.

    Returns:
        The matching ``User`` instance, or ``None`` if not found.
    """
    return User.objects.filter(email__iexact=email).first()