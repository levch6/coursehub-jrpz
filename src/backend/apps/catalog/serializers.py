from rest_framework import serializers

from .models import Category, Course, Platform


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ("slug", "name", "base_url")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("slug", "name")


class CourseSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "url",
            "platform",
            "category",
            "price",
            "currency",
            "rating",
            "language",
            "level",
            "is_available",
            "updated_at",
        )
