from django.urls import path
from .admin_views import ApplicationApproveView, ApplicationRejectView

urlpatterns = [
    path("applications/<int:pk>/approve/", ApplicationApproveView.as_view()),
    path("applications/<int:pk>/reject/", ApplicationRejectView.as_view()),
]
