"""API views for user authentication, profile management, and JWT handling.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.mixins import APIResponseMixin
from apps.core.response import api_response
from apps.core.throttles import LoginRateThrottle

from .serializers import ChangePasswordSerializer, UserRegistrationSerializer, UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Create a new user account.

    **Access:** public (no authentication required).

    **Fields for creation:**

      - ``email`` (string, required) — valid email, used for login
      - ``password`` (string, required) — at least 8 characters
      - ``password_confirm`` (string, required) — must match password
      - ``first_name`` (string, optional)
      - ``last_name`` (string, optional)
    """

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return api_response(
            success=True,
            data=UserSerializer(user).data,
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """Login with email and password to obtain JWT tokens.

    **Access:** public (no authentication required).

    **Rate-limited:** 5 attempts per minute.

    **Request fields:**

      - ``email`` (string, required) — registered email address
      - ``password`` (string, required) — account password

    **Returns:** ``access`` token (15 min) and ``refresh`` token (7 days).
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return api_response(success=True, data=response.data)
        return response


class RefreshTokenView(TokenRefreshView):
    """Public endpoint for refreshing an expired access token."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return api_response(success=True, data=response.data)
        return response


class UserProfileView(APIResponseMixin, generics.RetrieveUpdateAPIView):
    """View and update the authenticated user's own profile.

    Uses ``api_response`` wrapper for consistent response format.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(success=True, data=serializer.data)


class ChangePasswordView(generics.GenericAPIView):
    """Authenticated endpoint for changing the current user's password."""

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return api_response(success=True, data={"message": "Password changed successfully"})
