# users/urls.py
from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import RegisterView, me, LogoutView

# Public SimpleJWT views (use email+password since USERNAME_FIELD = "email")
class PublicTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)


class PublicTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)


class PublicTokenVerifyView(TokenVerifyView):
    permission_classes = (AllowAny,)


urlpatterns = [
    # ---------- AUTH ----------
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", PublicTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", PublicTokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/verify/", PublicTokenVerifyView.as_view(), name="auth-verify"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),

    # ---------- CURRENT USER ----------
    path("auth/me/", me, name="auth-me"),
]
