"""Custom user model using email as the unique identifier instead of username."""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    """Manager for creating regular users and superusers with email auth."""

    def normalize_email(self, email):
        """Lowercase the email in addition to Django's default normalisation."""
        return super().normalize_email(email).lower()

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user.

        Args:
            email: Unique email address (required).
            password: Plain-text password (will be hashed).
            **extra_fields: Additional model fields.

        Raises:
            ValueError: If email is empty.
        """
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with staff and superuser flags.

        Args:
            email: Unique email address.
            password: Plain-text password.
            **extra_fields: Additional model fields.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the primary identifier.

    Replaces Django's default ``username`` field with ``email``.
    Includes timestamps for creation and last update.
    """

    email = models.EmailField("email", unique=True)
    first_name = models.CharField("first name", max_length=150, blank=True)
    last_name = models.CharField("last name", max_length=150, blank=True)
    is_active = models.BooleanField("active", default=True)
    is_staff = models.BooleanField("staff", default=False)
    created_at = models.DateTimeField("created", auto_now_add=True)
    updated_at = models.DateTimeField("updated", auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email
