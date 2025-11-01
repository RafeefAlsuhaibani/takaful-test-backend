from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Program
from .serializers import ProgramListSerializer, ProgramDetailSerializer

@extend_schema(tags=["Programs"])
class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "kind": ["exact"],
        "status": ["exact"],
        "service_category": ["exact"],
        "region": ["icontains"],
        "city": ["icontains"],
        "is_active": ["exact"],
        "scheduled_date": ["gte", "lte"],
    }
    search_fields = ["name", "short_summary", "description"]
    ordering_fields = ["scheduled_date", "name", "created_at"]
    ordering = ["-scheduled_date"]

    def get_queryset(self):
        qs = Program.objects.all().prefetch_related("audiences", "requirements")
        kind = self.request.query_params.get("kind", "service")
        qs = qs.filter(kind=kind, is_active=True)

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(service_category=category)

        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(scheduled_date__gte=date_from)
        if date_to:
            qs = qs.filter(scheduled_date__lte=date_to)
        return qs

    def get_serializer_class(self):
        return ProgramDetailSerializer if self.action == "retrieve" else ProgramListSerializer
