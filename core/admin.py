from django.contrib import admin
from .models import Program, ProgramRequirement, AudienceSegment

class ProgramRequirementInline(admin.TabularInline):
    model = ProgramRequirement
    extra = 1

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "service_category", "status", "city", "region", "scheduled_date", "is_active")
    list_filter = ("kind", "service_category", "status", "is_active", "region", "city")
    search_fields = ("name", "description", "sponsor_name")
    inlines = [ProgramRequirementInline]
    filter_horizontal = ("audiences",)

@admin.register(AudienceSegment)
class AudienceSegmentAdmin(admin.ModelAdmin):
    search_fields = ("name",)
