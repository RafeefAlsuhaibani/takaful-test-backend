# users/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.translation import gettext_lazy as _
import re

from volunteers.models import VolunteerProfile, Skill, Interest

User = get_user_model()


def normalize_sa_phone(s: str) -> str:
    """Return phone in +9665XXXXXXXX format."""
    if not s:
        return s
    s = s.strip().replace(" ", "")
    # +9665XXXXXXXX
    if re.fullmatch(r"\+9665\d{8}", s):
        return s
    # 05XXXXXXXX -> +9665XXXXXXXX
    if re.fullmatch(r"05\d{8}", s):
        return "+966" + s[1:]
    # 5XXXXXXXX -> +9665XXXXXXXX
    if re.fullmatch(r"5\d{8}", s):
        return "+966" + s
    return s  # let validators raise if wrong


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")


class RegisterSerializer(serializers.Serializer):
    # User
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message=_("البريد الإلكتروني مستخدم مسبقًا"))]
    )
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=8)

    # VolunteerProfile (required to match your model)
    national_id = serializers.CharField(max_length=10)
    gender = serializers.ChoiceField(choices=[("female", "female"), ("male", "male")])
    age = serializers.IntegerField(min_value=14, max_value=100)

    # Optional fields
    region = serializers.CharField(max_length=100, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    education_level = serializers.CharField(max_length=100, required=False, allow_blank=True)
    available_days = serializers.ListField(child=serializers.CharField(), required=False)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    interests = serializers.ListField(child=serializers.CharField(), required=False)

    # --- Field-level validation / normalization ---
    def validate_phone(self, value):
        value = normalize_sa_phone(value)
        # reuse model-level validator for final check
        from volunteers.models import sa_phone_validator
        sa_phone_validator(value)
        return value

    def validate_national_id(self, value):
        value = (value or "").strip()
        from volunteers.models import national_id_validator
        national_id_validator(value)  # ensures exactly 10 digits
        return value

    # --- Create user + profile ---
    def create(self, validated_data):
        # extract core user fields
        full_name = validated_data.pop("full_name")
        email = validated_data.pop("email")
        phone = validated_data.pop("phone")
        password = validated_data.pop("password")

        # pull optional lists before creating profile
        skills = validated_data.pop("skills", [])
        interests = validated_data.pop("interests", [])

        # create user (email as username)
        user = User(username=email, email=email)
        # only set if your custom User has those fields
        if hasattr(user, "first_name") and " " in full_name:
            user.first_name = full_name.split(" ", 1)[0]
            user.last_name = full_name.split(" ", 1)[1]
        elif hasattr(user, "first_name"):
            user.first_name = full_name

        user.set_password(password)
        user.save()

        # create volunteer profile
        profile = VolunteerProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            national_id=validated_data.get("national_id"),
            gender=validated_data.get("gender"),
            age_years=validated_data.get("age"),
            region=validated_data.get("region", ""),
            city=validated_data.get("city", ""),
            education_level=validated_data.get("education_level", ""),
        )

        # attach tags (create if missing)
        for name in skills:
            s, _ = Skill.objects.get_or_create(name=name.strip())
            profile.skills.add(s)
        for name in interests:
            i, _ = Interest.objects.get_or_create(name=name.strip())
            profile.interests.add(i)

        return user
