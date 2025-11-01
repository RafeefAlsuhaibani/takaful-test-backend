from django.apps import apps
from rest_framework import serializers
import re

# Lazy model lookups avoid circular imports at import-time
Skill = apps.get_model("volunteers", "Skill")
Interest = apps.get_model("volunteers", "Interest")
VolunteerProfile = apps.get_model("volunteers", "VolunteerProfile")
VolunteerApplication = apps.get_model("volunteers", "VolunteerApplication")
VolunteerTask = apps.get_model("volunteers", "VolunteerTask")
VolunteerTaskItem = apps.get_model("volunteers", "VolunteerTaskItem")
Program = apps.get_model("core", "Program")

# import validators from the model via apps as well
# (we can read them off the model module after apps are ready)
# But simpler: just re-import safely from the model module at runtime inside funcs if needed.
# We'll inline normalization and then call the validators via the model module.
def normalize_sa_phone(s: str) -> str:
    """Normalize SA mobile to +9665XXXXXXXX."""
    if not s:
        return s
    phone = s.replace(" ", "").strip()
    if re.fullmatch(r"\+9665\d{8}", phone):
        return phone
    if re.fullmatch(r"05\d{8}", phone):
        return "+966" + phone[1:]
    if re.fullmatch(r"5\d{8}", phone):
        return "+966" + phone
    return phone  # let validators handle mismatch


# ---------- basic reference serializers ----------
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name")


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ("id", "name")


# ---------- inline, minimal Program serializer (avoid importing core.serializers) ----------
class ProgramMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ("id", "name")


# ---------- profile serializers ----------
class VolunteerProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    interests = InterestSerializer(many=True, read_only=True)

    class Meta:
        model = VolunteerProfile
        fields = (
            "id",
            "full_name",
            "national_id",
            "gender",
            "age_years",
            "phone",
            "region",
            "city",
            "joined_hijri",
            "education_level",
            "institution",
            "major",
            "bio",
            "skills",
            "interests",
            "total_hours",
            "rating_avg",
            "points",
        )

    # normalize + validate
    def validate_phone(self, value: str) -> str:
        from volunteers.models import sa_phone_validator  # safe here
        v = normalize_sa_phone(value)
        sa_phone_validator(v)
        return v

    def validate_national_id(self, value: str) -> str:
        from volunteers.models import national_id_validator  # safe here
        national_id_validator(value)
        return value


class VolunteerProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerProfile
        fields = (
            "full_name",
            "gender",
            "age_years",
            "phone",
            "region",
            "city",
            "joined_hijri",
            "education_level",
            "institution",
            "major",
            "bio",
        )

    def validate_phone(self, value: str) -> str:
        from volunteers.models import sa_phone_validator
        v = normalize_sa_phone(value)
        sa_phone_validator(v)
        return v


# ---------- applications / tasks ----------
class VolunteerApplicationSerializer(serializers.ModelSerializer):
    program = ProgramMiniSerializer(read_only=True)

    class Meta:
        model = VolunteerApplication
        fields = (
            "id",
            "status",
            "applied_at",
            "approved_at",
            "start_date",
            "due_date",
            "planned_hours",
            "actual_hours",
            "org_rating",
            "volunteer_note",
            "program",
            "profile_snapshot",  # ⬅️ NEW FIELD: snapshot of volunteer info at apply time
        )
        read_only_fields = fields

class VolunteerTaskItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerTaskItem
        fields = ("id", "text", "is_done", "order")


class VolunteerTaskSerializer(serializers.ModelSerializer):
    items = VolunteerTaskItemSerializer(many=True, read_only=True)

    class Meta:
        model = VolunteerTask
        fields = (
            "id",
            "title",
            "description",
            "status",
            "progress_percent",
            "planned_hours",
            "due_date",
            "location_city",
            "location_region",
            "application",
            "items",
        )
