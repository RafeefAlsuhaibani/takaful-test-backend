from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .models import Program, InitiativeKind, InitiativeStatus

def _check_kind_permission(user, program):
    is_pm = user.groups.filter(name="project_manager").exists()
    is_sm = user.groups.filter(name="service_manager").exists()
    if program.kind == InitiativeKind.PROJECT and not is_pm:
        raise PermissionDenied("Project manager role required.")
    if program.kind == InitiativeKind.SERVICE and not is_sm:
        raise PermissionDenied("Service manager role required.")

@extend_schema(tags=["Admin - Programs"])
class ProgramPublishView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk: int):
        try:
            program = Program.objects.get(pk=pk)
        except Program.DoesNotExist:
            raise NotFound("Program not found.")
        _check_kind_permission(request.user, program)
        program.is_active = True
        program.status = InitiativeStatus.PUBLISHED
        program.save(update_fields=["is_active", "status"])
        return Response({"ok": True, "id": program.id, "status": program.status, "is_active": program.is_active})

@extend_schema(tags=["Admin - Programs"])
class ProgramUnpublishView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk: int):
        try:
            program = Program.objects.get(pk=pk)
        except Program.DoesNotExist:
            raise NotFound("Program not found.")
        _check_kind_permission(request.user, program)
        program.is_active = False
        program.save(update_fields=["is_active"])
        return Response({"ok": True, "id": program.id, "status": program.status, "is_active": program.is_active})

@extend_schema(tags=["Admin - Programs"])
class ProgramMarkDoneView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk: int):
        try:
            program = Program.objects.get(pk=pk)
        except Program.DoesNotExist:
            raise NotFound("Program not found.")
        _check_kind_permission(request.user, program)
        program.status = InitiativeStatus.COMPLETED
        program.save(update_fields=["status"])
        return Response({"ok": True, "id": program.id, "status": program.status})
