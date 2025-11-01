from rest_framework import serializers
from .models import Program, ProgramRequirement, AudienceSegment


class AudienceSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudienceSegment
        fields = ("id", "name")


class ProgramRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramRequirement
        fields = ("id", "text", "order")


class ProgramListSerializer(serializers.ModelSerializer):
    """Compact card view for lists."""
    progress_volunteers = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = (
            "id",
            "kind",
            "name",
            "short_summary",
            "status",
            "service_category",
            "city",
            "region",
            "scheduled_date",
            "sponsor_name",
            "allow_volunteers",
            "volunteers_required",
            "volunteers_committed",
            "allow_donations",
            "target_units_label",
            "target_units",
            "target_beneficiaries",
            "progress_volunteers",
        )

    def get_progress_volunteers(self, obj):
        if obj.volunteers_required:
            return min(100, int(obj.volunteers_committed * 100 / obj.volunteers_required))
        return 0


class ProgramDetailSerializer(ProgramListSerializer):
    """Full detail for the modal page."""
    audiences = AudienceSegmentSerializer(many=True, read_only=True)
    requirements = ProgramRequirementSerializer(many=True, read_only=True)

    class Meta(ProgramListSerializer.Meta):
        fields = ProgramListSerializer.Meta.fields + (
            "description",
            "audiences",
            "requirements",
        )
