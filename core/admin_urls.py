from django.urls import path
from .admin_views import ProgramPublishView, ProgramUnpublishView, ProgramMarkDoneView

urlpatterns = [
    path("programs/<int:pk>/publish/", ProgramPublishView.as_view()),
    path("programs/<int:pk>/unpublish/", ProgramUnpublishView.as_view()),
    path("programs/<int:pk>/mark_done/", ProgramMarkDoneView.as_view()),
]
