# core/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProgramViewSet

router = DefaultRouter()
router.register(r"", ProgramViewSet, basename="program")

urlpatterns = router.urls
