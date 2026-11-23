"""Пошук і фільтрація курсів (ФВ-09, ФВ-10, ФВ-11)."""

import django_filters
from django.db.models import F, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

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


class NullsLastOrderingFilter(OrderingFilter):
    """Сортування за параметром ``ordering``, за якого порожні значення завжди в кінці.

    Без цього PostgreSQL під час сортування за спаданням ставить курси без рейтингу
    чи ціни на початок списку.
    """

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if not ordering:
            return queryset
        return queryset.order_by(*(self._nulls_last(term) for term in ordering))

    @staticmethod
    def _nulls_last(term: str):
        if term.startswith("-"):
            return F(term[1:]).desc(nulls_last=True)
        return F(term).asc(nulls_last=True)


COURSE_FILTER_BACKENDS = [DjangoFilterBackend, NullsLastOrderingFilter]
