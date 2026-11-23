from rest_framework import viewsets

from .filters import CourseFilter
from .models import Category, Course
from .serializers import CategorySerializer, CourseSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Список і сторінка курсу (ФВ-08, ФВ-12). Приховані курси користувачам не видно."""

    serializer_class = CourseSerializer
    filterset_class = CourseFilter
    ordering_fields = ["price", "rating", "title", "updated_at"]

    def get_queryset(self):
        return Course.objects.filter(is_hidden=False).select_related("platform", "category")


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    pagination_class = None
    lookup_field = "slug"
