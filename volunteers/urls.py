from django.urls import path
from .views import (
    MeProfileView,
    MeApplicationsView,
    MeTasksView,
    ApplyView,
    SkillsListView,
    InterestsListView,
    MeSetSkillsView,
    MeSetInterestsView,
    MeWithdrawApplicationView,
    MeUpdateApplicationNoteView,
    MeLogHoursView,
    MeTaskItemsView,
    MeToggleTaskItemView,
    MeUpdateTaskProgressView,
)

app_name = "volunteers"

urlpatterns = [
    # --- Profile ---
    path("volunteers/me/profile/", MeProfileView.as_view(), name="me-profile"),
    path("volunteers/me/profile/skills/", MeSetSkillsView.as_view(), name="me-profile-skills"),
    path("volunteers/me/profile/interests/", MeSetInterestsView.as_view(), name="me-profile-interests"),

    # --- Lookups ---
    path("lookups/skills/", SkillsListView.as_view(), name="skills"),
    path("lookups/interests/", InterestsListView.as_view(), name="interests"),
    path("skills/", SkillsListView.as_view(), name="skills-legacy"),
    path("interests/", InterestsListView.as_view(), name="interests-legacy"),

    # --- Applications ---
    path("applications/apply/", ApplyView.as_view(), name="applications-apply"),
    path("volunteers/me/applications/", MeApplicationsView.as_view(), name="me-applications"),
    path("applications/<int:app_id>/withdraw/", MeWithdrawApplicationView.as_view(), name="applications-withdraw"),
    path("applications/<int:app_id>/note/", MeUpdateApplicationNoteView.as_view(), name="applications-note"),
    path("applications/<int:app_id>/log_hours/", MeLogHoursView.as_view(), name="applications-log-hours"),
    path("applications/<int:app_id>/hours/", MeLogHoursView.as_view(), name="applications-hours"),

    # --- Tasks ---
    path("volunteers/me/tasks/", MeTasksView.as_view(), name="me-tasks"),
    path("volunteers/me/tasks/<int:task_id>/items/", MeTaskItemsView.as_view(), name="me-task-items"),
    path("volunteers/me/tasks/<int:task_id>/items/<int:item_id>/", MeToggleTaskItemView.as_view(), name="me-task-item-update"),
    path("volunteers/me/tasks/<int:task_id>/items/<int:item_id>/toggle/", MeToggleTaskItemView.as_view(), name="me-task-item-toggle-legacy"),
    path("volunteers/me/tasks/<int:task_id>/progress/", MeUpdateTaskProgressView.as_view(), name="me-task-progress"),
]
