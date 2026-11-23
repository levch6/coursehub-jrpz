from rest_framework import serializers

from apps.catalog.models import Course
from apps.collection.models import ScrapeRun


class ScrapeRunSerializer(serializers.ModelSerializer):
    platform = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = ScrapeRun
        fields = (
            "id",
            "platform",
            "status",
            "started_at",
            "finished_at",
            "courses_created",
            "courses_updated",
            "courses_unavailable",
            "error",
        )


class CourseModerationSerializer(serializers.ModelSerializer):
    """Редагування й приховування курсів адміністратором (ФВ-23)."""

    class Meta:
        model = Course
        fields = ("id", "title", "description", "category", "is_hidden")
