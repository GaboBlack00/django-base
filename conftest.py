"""Global pytest configuration: fixtures, logging suppression, and throttle override.

All fixtures defined here are automatically available to every test in
the project (both ``tests/`` and ``apps/*/tests/``).
"""

import logging
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


def pytest_configure(config):
    """Suppress noisy loggers during tests and raise throttle limits."""
    logging.getLogger("api").setLevel(logging.CRITICAL)
    logging.getLogger("django.request").setLevel(logging.CRITICAL)
    logging.getLogger("django").setLevel(logging.CRITICAL)

    from django.conf import settings
    rates = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {})
    for scope in rates:
        rates[scope] = "10000/m"


@pytest.fixture
def api_client():
    """Return a DRF ``APIClient`` instance for simulating HTTP requests."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a regular (non-staff) user."""
    return User.objects.create_user(email="test@example.com", password="securepass123")


@pytest.fixture
def admin_user(db):
    """Create and return a superuser with staff privileges."""
    return User.objects.create_superuser(email="admin@example.com", password="adminpass123")


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an ``APIClient`` pre-authenticated as a regular user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user_factory(db):
    """Factory fixture that creates users with arbitrary email addresses."""
    def factory(email, **kwargs):
        return User.objects.create_user(email=email, **kwargs)
    return factory