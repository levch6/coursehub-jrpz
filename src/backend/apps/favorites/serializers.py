from rest_framework import serializers

from apps.catalog.models import Course
from apps.catalog.serializers import CourseSerializer

from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_hidden=False), source="course", write_only=True
    )

    class Meta:
        model = Favorite
        fields = ("id", "course", "course_id", "created_at")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        favorite, _ = Favorite.objects.get_or_create(
            user=self.context["request"].user, course=validated_data["course"]
        )
        return favorite
