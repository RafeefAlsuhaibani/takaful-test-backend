from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from drf_spectacular.utils import extend_schema
from django.core.mail import send_mail
from django.conf import settings


from core.models import Program
from .models import (
    VolunteerProfile,
    VolunteerApplication,
    VolunteerTask,
    VolunteerTaskItem,
    ApplicationStatus,
    Skill,
    Interest,
)
from .serializers import (
    VolunteerProfileSerializer,
    VolunteerProfileUpdateSerializer,
    VolunteerApplicationSerializer,
    VolunteerTaskSerializer,
    VolunteerTaskItemSerializer,
    SkillSerializer,
    InterestSerializer,
)


@extend_schema(tags=["Volunteers"])
class MeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = (
                VolunteerProfile.objects
                .select_related("user")
                .prefetch_related("skills", "interests")
                .get(user=request.user)
            )
        except VolunteerProfile.DoesNotExist:
            raise NotFound("Volunteer profile does not exist.")
        return Response(VolunteerProfileSerializer(profile).data)

    def patch(self, request):
        try:
            profile = VolunteerProfile.objects.get(user=request.user)
        except VolunteerProfile.DoesNotExist:
            raise NotFound("Volunteer profile does not exist.")
        ser = VolunteerProfileUpdateSerializer(profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(VolunteerProfileSerializer(profile).data)


@extend_schema(tags=["Volunteers"])
class SkillsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Skill.objects.all().order_by("name")
        return Response(SkillSerializer(qs, many=True).data)


@extend_schema(tags=["Volunteers"])
class InterestsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Interest.objects.all().order_by("name")
        return Response(InterestSerializer(qs, many=True).data)


@extend_schema(tags=["Volunteers"])
class MeSetSkillsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data.get("ids", [])
        try:
            profile = VolunteerProfile.objects.get(user=request.user)
        except VolunteerProfile.DoesNotExist:
            raise NotFound("Volunteer profile does not exist.")
        skills = list(Skill.objects.filter(id__in=ids))
        profile.skills.set(skills)
        return Response({"ok": True, "skill_ids": [s.id for s in skills]})


@extend_schema(tags=["Volunteers"])
class MeSetInterestsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data.get("ids", [])
        try:
            profile = VolunteerProfile.objects.get(user=request.user)
        except VolunteerProfile.DoesNotExist:
            raise NotFound("Volunteer profile does not exist.")
        interests = list(Interest.objects.filter(id__in=ids))
        profile.interests.set(interests)
        return Response({"ok": True, "interest_ids": [i.id for i in interests]})


@extend_schema(tags=["Volunteers"])
class MeApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_param = request.query_params.get("status")
        qs = (
            VolunteerApplication.objects
            .select_related("program", "profile")
            .filter(profile__user=request.user)
        )
        if status_param:
            qs = qs.filter(status=status_param)
        return Response(VolunteerApplicationSerializer(qs, many=True).data)



@extend_schema(tags=["Volunteers"])
class ApplyView(APIView):
    """
    Lightweight apply endpoint:
    - tolerates multiple profiles (takes the first one)
    - stores a minimal snapshot (or empty)
    - sends confirmation email if possible
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        program_id = request.data.get("program_id")
        if not program_id:
            return Response({"detail": "program_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1) Program must exist and be active
        try:
            program = Program.objects.get(pk=program_id, is_active=True)
        except Program.DoesNotExist:
            return Response({"detail": "Program not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

        # 2) Try to get *one* profile for this user, but be tolerant
        profiles_qs = VolunteerProfile.objects.filter(user=request.user).order_by("id")
        profile = profiles_qs.first()
        if not profile:
            return Response({"detail": "Volunteer profile does not exist yet."}, status=status.HTTP_404_NOT_FOUND)

        # 3) Minimal snapshot (you said “we didn’t finish working on profiles yet”)
        #    → keep it tiny for now
        snapshot = {
            "user": {
                "id": request.user.id,
                "email": request.user.email,
            },
            "profile_id": profile.id,
            "program_id": program.id,
        }

        # 4) Create / return application
        try:
            app, created = VolunteerApplication.objects.get_or_create(
                program=program,
                profile=profile,
                defaults={
                    "status": ApplicationStatus.APPLIED,
                    "profile_snapshot": snapshot,   # minimal snapshot
                },
            )
        except Exception:
            # in case of some weird integrity error
            return Response({"detail": "You already applied to this program."}, status=status.HTTP_400_BAD_REQUEST)

        # 5) Send confirmation email ONLY on first apply
        if created and request.user.email:
            subject = "تم استلام طلبك للمشاركة في المشروع"
            message = (
                f"مرحبًا،\n\n"
                f"تم استلام طلبك للمشاركة في مشروع «{program.name}».\n"
                f"سنقوم بمراجعته وسيصلك إشعار عند القبول.\n\n"
                f"منصة تكافل."
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,  # لا نكسر الـ API لو البريد ما اشتغل
                )
            except Exception:
                # نسيبه ساكتين حالياً
                pass

        # 6) Response
        return Response(
            {
                "id": app.id,
                "status": app.status,
                "program": {"id": program.id, "name": program.name},
                "created": created,
                "message": "تم استلام طلبك بنجاح."
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
@extend_schema(tags=["Volunteers"])
class MeWithdrawApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, app_id: int):
        try:
            app = VolunteerApplication.objects.select_related("profile__user").get(pk=app_id)
        except VolunteerApplication.DoesNotExist:
            raise NotFound("Application not found.")
        if app.profile.user_id != request.user.id:
            raise PermissionDenied("Not your application.")
        app.status = ApplicationStatus.WITHDRAWN
        app.save(update_fields=["status"])
        return Response({"ok": True, "id": app.id, "status": app.status})


@extend_schema(tags=["Volunteers"])
class MeUpdateApplicationNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, app_id: int):
        note = request.data.get("volunteer_note", "")
        try:
            app = VolunteerApplication.objects.select_related("profile__user").get(pk=app_id)
        except VolunteerApplication.DoesNotExist:
            raise NotFound("Application not found.")
        if app.profile.user_id != request.user.id:
            raise PermissionDenied("Not your application.")
        app.volunteer_note = note
        app.save(update_fields=["volunteer_note"])
        return Response({"ok": True, "id": app.id, "volunteer_note": app.volunteer_note})


@extend_schema(tags=["Volunteers"])
class MeLogHoursView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, app_id: int):
        hours = int(request.data.get("hours", 0))
        if hours <= 0:
            return Response({"detail": "hours must be > 0"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            app = VolunteerApplication.objects.select_related("profile__user").get(pk=app_id)
        except VolunteerApplication.DoesNotExist:
            raise NotFound("Application not found.")
        if app.profile.user_id != request.user.id:
            raise PermissionDenied("Not your application.")
        app.actual_hours = app.actual_hours + hours
        app.save(update_fields=["actual_hours"])
        vp = app.profile
        vp.total_hours = vp.total_hours + hours
        vp.save(update_fields=["total_hours"])
        return Response({
            "ok": True,
            "application_id": app.id,
            "actual_hours": app.actual_hours,
            "profile_total_hours": vp.total_hours
        })


@extend_schema(tags=["Volunteers"])
class MeTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_param = request.query_params.get("status")
        qs = (
            VolunteerTask.objects
            .select_related("application", "application__program", "application__profile")
            .filter(application__profile__user=request.user)
        )
        if status_param:
            qs = qs.filter(status=status_param)
        return Response(VolunteerTaskSerializer(qs, many=True).data)


@extend_schema(tags=["Volunteers"])
class MeTaskItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id: int):
        try:
            task = VolunteerTask.objects.select_related("application__profile__user").get(pk=task_id)
        except VolunteerTask.DoesNotExist:
            raise NotFound("Task not found.")
        if task.application.profile.user_id != request.user.id:
            raise PermissionDenied("Not your task.")
        items = task.items.all().order_by("order", "id")
        return Response(VolunteerTaskItemSerializer(items, many=True).data)


@extend_schema(tags=["Volunteers"])
class MeToggleTaskItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id: int, item_id: int):
        try:
            item = (
                VolunteerTaskItem.objects
                .select_related("task__application__profile__user")
                .get(pk=item_id, task_id=task_id)
            )
        except VolunteerTaskItem.DoesNotExist:
            raise NotFound("Item not found.")
        if item.task.application.profile.user_id != request.user.id:
            raise PermissionDenied("Not your task item.")
        is_done = bool(request.data.get("is_done", True))
        item.is_done = is_done
        item.save(update_fields=["is_done"])
        return Response({"ok": True, "item_id": item.id, "is_done": item.is_done})


@extend_schema(tags=["Volunteers"])
class MeUpdateTaskProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id: int):
        try:
            task = VolunteerTask.objects.select_related("application__profile__user").get(pk=task_id)
        except VolunteerTask.DoesNotExist:
            raise NotFound("Task not found.")
        if task.application.profile.user_id != request.user.id:
            raise PermissionDenied("Not your task.")
        fields = {}
        if "progress_percent" in request.data:
            pp = int(request.data["progress_percent"])
            if pp < 0 or pp > 100:
                return Response({"detail": "progress_percent must be 0..100"}, status=status.HTTP_400_BAD_REQUEST)
            fields["progress_percent"] = pp
        if "status" in request.data:
            fields["status"] = request.data["status"]
        if not fields:
            return Response({"detail": "no fields to update"}, status=status.HTTP_400_BAD_REQUEST)
        for k, v in fields.items():
            setattr(task, k, v)
        task.save(update_fields=list(fields.keys()))
        return Response(VolunteerTaskSerializer(task).data)
