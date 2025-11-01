# volunteers/admin.py
from django.contrib import admin
from django.apps import apps

# Lazy-load models to avoid import-time errors
Skill = apps.get_model("volunteers", "Skill")
Interest = apps.get_model("volunteers", "Interest")
VolunteerProfile = apps.get_model("volunteers", "VolunteerProfile")
VolunteerApplication = apps.get_model("volunteers", "VolunteerApplication")
VolunteerTask = apps.get_model("volunteers", "VolunteerTask")
VolunteerTaskItem = apps.get_model("volunteers", "VolunteerTaskItem")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name")


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name")


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "gender", "age_years", "phone", "city", "region", "total_hours", "points")
    list_filter = ("gender", "education_level", "city", "region")
    search_fields = ("full_name", "national_id", "phone", "user__email")
    filter_horizontal = ("skills", "interests")


@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "program", "profile", "status", "applied_at", "due_date", "planned_hours", "actual_hours")
    list_filter = ("status", "applied_at", "due_date", "program")
    search_fields = ("profile__full_name", "program__name")


class VolunteerTaskItemInline(admin.TabularInline):
    model = VolunteerTaskItem
    extra = 0


@admin.register(VolunteerTask)
class VolunteerTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "application", "status", "progress_percent", "due_date", "location_city")
    list_filter = ("status", "due_date")
    search_fields = ("title", "application__profile__full_name", "application__program__name")
    inlines = [VolunteerTaskItemInline]
