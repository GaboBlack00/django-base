"""DRF serializers for user registration, profile, and password change."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .services import UserService

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Validate and create a new user account.

    Expects ``password`` and ``password_confirm`` to match; delegates
    persistence to ``UserService``.
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text="At least 8 characters. Must not be too common or entirely numeric.",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Must match the password field.",
    )

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm", "first_name", "last_name"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return UserService.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Public profile representation of a user (read-only for most fields)."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_active", "created_at"]
        read_only_fields = ["id", "email", "is_active", "created_at"]


class ChangePasswordSerializer(serializers.Serializer):
    """Validate old and new password for the authenticated user.

    ``old_password`` is checked against the current user's stored hash.
    """

    old_password = serializers.CharField(
        write_only=True,
        help_text="Current password for verification.",
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text="New password. At least 8 characters.",
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
