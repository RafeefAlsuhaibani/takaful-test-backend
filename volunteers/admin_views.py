from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .models import VolunteerApplication, ApplicationStatus
from core.models import InitiativeKind

def _check_app_permission(user, app):
    is_pm = user.groups.filter(name="project_manager").exists()
    is_sm = user.groups.filter(name="service_manager").exists()
    if app.program.kind == InitiativeKind.PROJECT and not is_pm:
        raise PermissionDenied("Project manager role required.")
    if app.program.kind == InitiativeKind.SERVICE and not is_sm:
        raise PermissionDenied("Service manager role required.")

@extend_schema(tags=["Admin - Applications"])
class ApplicationApproveView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk: int):
        try:
            app = VolunteerApplication.objects.select_related("program").get(pk=pk)
        except VolunteerApplication.DoesNotExist:
            raise NotFound("Application not found.")
        _check_app_permission(request.user, app)
        app.status = ApplicationStatus.ACCEPTED
        app.approved_at = timezone.now()
        app.save(update_fields=["status", "approved_at"])
        return Response({"ok": True, "id": app.id, "status": app.status})

@extend_schema(tags=["Admin - Applications"])
class ApplicationRejectView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk: int):
        try:
            app = VolunteerApplication.objects.select_related("program").get(pk=pk)
        except VolunteerApplication.DoesNotExist:
            raise NotFound("Application not found.")
        _check_app_permission(request.user, app)
        app.status = ApplicationStatus.REJECTED
        app.save(update_fields=["status"])
        return Response({"ok": True, "id": app.id, "status": app.status})
