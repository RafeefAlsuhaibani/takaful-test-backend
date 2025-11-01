# users/views.py
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
)

from .serializers import RegisterSerializer, UserPublicSerializer
from volunteers.serializers import VolunteerProfileSerializer

User = get_user_model()


# ------------------- AUTH: REGISTER (SIGNUP) -------------------
@extend_schema(
    tags=["v1"],
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(response=UserPublicSerializer, description="Created"),
        400: OpenApiResponse(description="Validation error"),
    },
    examples=[
        OpenApiExample(
            "Register payload",
            value={
                "full_name": "Rafeef Alsubhi",
                "email": "r@example.com",
                "phone": "0501234567",
                "password": "StrongPass123",
                "national_id": "1234567890",
                "gender": "female",
                "age": 23,
                "region": "Qassim",
                "city": "Buraidah",
                "education_level": "bachelor",
                "skills": ["تصميم"],
                "interests": ["توعية"],
            },
            request_only=True,
        )
    ],
)
class RegisterView(APIView):
    """
    Creates the user account and immediately returns JWT tokens.
    NOTE: Login is handled by SimpleJWT at /auth/login/ (PublicTokenObtainPairView in urls.py).
    """
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # serializer should handle normalization/uniqueness & profile creation if desired

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserPublicSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


# ------------------- PROFILE: ME -------------------
@extend_schema(
    tags=["v1"],
    responses={
        200: OpenApiResponse(
            description="Current user with volunteer profile (if any)"
        )
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    """
    Returns the authenticated user and their volunteer profile (if exists).
    """
    user = request.user
    profile = getattr(user, "volunteer_profile", None)
    return Response(
        {
            "id": user.id,
            "email": getattr(user, "email", ""),
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "volunteer_profile": VolunteerProfileSerializer(profile).data if profile else None,
        },
        status=status.HTTP_200_OK,
    )


# ------------------- LOGOUT (BLACKLIST REFRESH) -------------------
# Works only if 'rest_framework_simplejwt.token_blacklist' is in INSTALLED_APPS and migrated.
try:
    from rest_framework_simplejwt.tokens import TokenError  # noqa: F401

    @extend_schema(
        tags=["v1"],
        request={
            "type": "object",
            "properties": {"refresh": {"type": "string"}},
            "required": ["refresh"],
        },
        responses={
            205: OpenApiResponse(description="Refresh token blacklisted"),
            400: OpenApiResponse(description="Missing/invalid refresh token"),
        },
        examples=[
            OpenApiExample(
                "Logout payload",
                value={"refresh": "eyJhbGciOiJIUzI1NiIs..."},
                request_only=True,
            )
        ],
    )
    class LogoutView(APIView):
        """
        Blacklists the provided refresh token. Access tokens expire on their own.
        """
        permission_classes = [permissions.IsAuthenticated]

        def post(self, request):
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Missing refresh token."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_205_RESET_CONTENT)

except Exception:
    # If blacklist app is not installed, expose a graceful 501 view instead.
    @extend_schema(
        tags=["v1"],
        responses={501: OpenApiResponse(description="Token blacklist not enabled")},
    )
    class LogoutView(APIView):
        permission_classes = [permissions.IsAuthenticated]

        def post(self, request):
            return Response(
                {"detail": "Token blacklist not enabled on server."},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )
