"""
URL configuration for takaful project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/users/", include(("users.urls", "users"), namespace="users")),
    path("api/v1/programs/", include(("core.urls", "core"), namespace="core")),
    path("api/v1/volunteers/", include(("volunteers.urls", "volunteers"), namespace="volunteers")),
    path("api/v1/admin/core/", include(("core.admin_urls", "core_admin"), namespace="core_admin")),
    path("api/v1/admin/volunteers/", include(("volunteers.admin_urls", "vol_admin"), namespace="vol_admin")),
]
