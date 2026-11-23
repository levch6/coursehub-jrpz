from rest_framework import serializers

from apps.catalog.models import Course
from apps.catalog.normalization import make_fingerprint
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
    """Редагування й приховування курсів адміністратором (ФВ-23).

    Зміна назви, опису чи категорії вмикає ``is_edited``, щоб наступний збір не
    затер правки. Явне ``is_edited: false`` повертає курс під оновлення збирачем.
    """

    EDITABLE_FIELDS = ("title", "description", "category")

    class Meta:
        model = Course
        fields = ("id", "title", "description", "category", "is_hidden", "is_edited")

    def update(self, instance, validated_data):
        if "is_edited" not in validated_data and any(
            field in validated_data for field in self.EDITABLE_FIELDS
        ):
            validated_data["is_edited"] = True
        if "title" in validated_data:
            validated_data["fingerprint"] = make_fingerprint(
                validated_data["title"], instance.language
            )
        return super().update(instance, validated_data)
