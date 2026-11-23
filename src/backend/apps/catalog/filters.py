"""Пошук і фільтрація курсів (ФВ-09, ФВ-10, ФВ-11)."""

import django_filters
from django.db.models import Q

from .models import Course


class CourseFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_query", label="Пошук за ключовими словами")
    platform = django_filters.CharFilter(field_name="platform__slug")
    category = django_filters.CharFilter(field_name="category__slug")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")

    class Meta:
        model = Course
        fields = ["platform", "category", "language", "level", "is_available"]

    def filter_query(self, queryset, _name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))
