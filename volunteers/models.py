from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Program

# ---------- Enums ----------
class Gender(models.TextChoices):
    MALE = "male", _("ذكر")
    FEMALE = "female", _("أنثى")


class EducationLevel(models.TextChoices):
    HS = "hs", _("ثانوي")
    DIPLOMA = "diploma", _("دبلوم")
    BACHELOR = "bachelor", _("بكالوريوس")
    MASTER = "master", _("ماجستير")
    PHD = "phd", _("دكتوراه")
    OTHER = "other", _("أخرى")


class ApplicationStatus(models.TextChoices):
    APPLIED = "applied", _("متقدم")
    ACCEPTED = "accepted", _("مقبول")
    IN_PROGRESS = "in_progress", _("قيد التنفيذ")
    ON_HOLD = "on_hold", _("معلقة")
    COMPLETED = "completed", _("مكتملة")
    WITHDRAWN = "withdrawn", _("منسحب")
    REJECTED = "rejected", _("مرفوض")


class TaskStatus(models.TextChoices):
    NEW = "new", _("جديدة")
    IN_PROGRESS = "in_progress", _("قيد التنفيذ")
    ON_HOLD = "on_hold", _("معلقة")
    DONE = "done", _("منجزة")
    CANCELLED = "cancelled", _("ملغاة")


# ---------- Reference ----------
class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class Interest(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


# ---------- Validators ----------
# National ID: 10 digits (Saudi)
national_id_validator = RegexValidator(
    regex=r"^\d{10}$",
    message=_("رقم الهوية يجب أن يكون مكونًا من 10 أرقام."),
)

# Saudi phone: 05XXXXXXXX or +9665XXXXXXXX
sa_phone_validator = RegexValidator(
    regex=r"^(\+9665\d{8}|05\d{8})$",
    message=_("رقم الجوال يجب أن يبدأ بـ 05 أو +9665 ويحتوي على 9 أرقام بعد ذلك."),
)


# ---------- Core ----------
class VolunteerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="volunteer_profile",
    )

    # Personal
    full_name = models.CharField(max_length=255)
    national_id = models.CharField(
        max_length=10,
        unique=True,
        validators=[national_id_validator],
        help_text=_("رقم الهوية الوطنية السعودية (10 أرقام)."),
    )
    gender = models.CharField(max_length=10, choices=Gender.choices)
    age_years = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(14), MaxValueValidator(100)]
    )
    phone = models.CharField(
        max_length=20,
        validators=[sa_phone_validator],
        help_text=_("رقم الجوال السعودي، مثل 05XXXXXXXX أو +9665XXXXXXXX"),
    )
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    joined_hijri = models.CharField(max_length=32, blank=True)

    # Education / experience
    education_level = models.CharField(
        max_length=20,
        choices=EducationLevel.choices,
        blank=True,
    )
    institution = models.CharField(max_length=255, blank=True)
    major = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)

    # Tags
    skills = models.ManyToManyField(Skill, blank=True, related_name="volunteers")
    interests = models.ManyToManyField(Interest, blank=True, related_name="volunteers")

    # Metrics
    total_hours = models.PositiveIntegerField(default=0)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    points = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["city", "region"]),
            models.Index(fields=["education_level"]),
        ]

    def __str__(self):
        return self.full_name


class VolunteerApplication(models.Model):
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name="volunteer_applications",
    )
    profile = models.ForeignKey(
        VolunteerProfile,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED,
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    planned_hours = models.PositiveIntegerField(default=0)
    actual_hours = models.PositiveIntegerField(default=0)

    org_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    volunteer_note = models.TextField(blank=True)

    # ✅ NEW: snapshot of the volunteer data at the time of applying
    # this is what we email / show to admins later even if the volunteer edits profile
    profile_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["program", "profile"],
                name="uniq_application_per_program",
            ),
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["applied_at"]),  # helps admin list "latest applications"
        ]

    def __str__(self):
        return f"{self.profile.full_name} → {self.program.name}"


class VolunteerTask(models.Model):
    application = models.ForeignKey(
        VolunteerApplication,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.NEW,
    )
    progress_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
    )
    order = models.PositiveSmallIntegerField(default=0)

    planned_hours = models.PositiveIntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    location_city = models.CharField(max_length=100, blank=True)
    location_region = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class VolunteerTaskItem(models.Model):
    task = models.ForeignKey(
        VolunteerTask,
        on_delete=models.CASCADE,
        related_name="items",
    )
    text = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text
