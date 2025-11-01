from django.db import models
from django.utils.translation import gettext_lazy as _

# ---------- Enums ----------
class InitiativeKind(models.TextChoices):
    SERVICE = "service", _("Service")
    PROJECT = "project", _("Project")

class InitiativeStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")
    UPCOMING = "upcoming", _("Upcoming")
    COMPLETED = "completed", _("Completed")

class ServiceCategory(models.TextChoices):
    ESSENTIAL = "essential", _("الخدمات الأساسية")
    COMMUNITY = "community", _("الخدمات المجتمعية")
    COMPLEMENTARY = "complementary", _("الخدمات المكملة")

# ---------- Reference ----------
class AudienceSegment(models.Model):
    """مثلاً: الأسر محدودة الدخل، الأرامل والمطلقات، كبار السن..."""
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name

# ---------- Main ----------
class Program(models.Model):
    """Unified entity for both Services & Projects (use kind to distinguish)."""
    kind = models.CharField(max_length=16, choices=InitiativeKind.choices, default=InitiativeKind.SERVICE)

    # Display
    name = models.CharField(max_length=255)
    short_summary = models.CharField(max_length=280, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=InitiativeStatus.choices, default=InitiativeStatus.PUBLISHED)
    is_active = models.BooleanField(default=True)

    # Service-only categorization (leave blank for projects)
    service_category = models.CharField(max_length=20, choices=ServiceCategory.choices, blank=True)

    # Location / date / sponsor
    region = models.CharField(max_length=100, blank=True)   # مثال: القصيم
    city = models.CharField(max_length=100, blank=True)     # مثال: بريدة
    scheduled_date = models.DateField(null=True, blank=True)
    sponsor_name = models.CharField(max_length=255, blank=True)

    # Participation & targets (for cards/progress)
    allow_volunteers = models.BooleanField(default=True)
    volunteers_required = models.PositiveIntegerField(default=0)
    volunteers_committed = models.PositiveIntegerField(default=0)

    allow_donations = models.BooleanField(default=True)
    target_units_label = models.CharField(max_length=64, blank=True)  # مثال: "سلة غذائية"
    target_units = models.PositiveIntegerField(default=0)
    target_beneficiaries = models.PositiveIntegerField(default=0)

    audiences = models.ManyToManyField(AudienceSegment, blank=True, related_name="programs")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["kind", "status"]),
            models.Index(fields=["service_category", "is_active"]),
            models.Index(fields=["scheduled_date"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

class ProgramRequirement(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="requirements")
    text = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.program.name} · {self.text}"
