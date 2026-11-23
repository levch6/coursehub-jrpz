"""Репозиторій курсів.

Абстракція ``CourseRepository`` відокремлює бізнес-логіку збору даних від ORM
(принцип інверсії залежностей). У тестах її замінює проста реалізація.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable

from django.utils.text import slugify

from .models import Category, Course, Platform
from .normalization import make_fingerprint
from .records import CourseRecord


class CourseRepository(ABC):
    @abstractmethod
    def ensure_platform(self, slug: str) -> Platform:
        """Повертає платформу за ідентифікатором, створюючи її за потреби."""

    @abstractmethod
    def upsert(self, platform: Platform, record: CourseRecord) -> tuple[Course, bool]:
        """Створює або оновлює курс. Друге значення: True, якщо курс створено."""

    @abstractmethod
    def mark_unavailable(self, platform: Platform, seen_external_ids: Iterable[str]) -> int:
        """Позначає недоступними курси платформи, яких немає серед ``seen_external_ids``."""


class DjangoCourseRepository(CourseRepository):
    def ensure_platform(self, slug: str) -> Platform:
        platform, _ = Platform.objects.get_or_create(
            slug=slug, defaults={"name": slug.replace("-", " ").title()}
        )
        return platform

    def upsert(self, platform: Platform, record: CourseRecord) -> tuple[Course, bool]:
        category = self._category(record.category)
        return Course.objects.update_or_create(
            platform=platform,
            external_id=record.external_id,
            defaults={
                "title": record.title,
                "description": record.description,
                "url": record.url,
                "price": record.price,
                "currency": record.currency,
                "rating": record.rating,
                "language": record.language,
                "level": record.level,
                "category": category,
                "fingerprint": make_fingerprint(record.title, record.language),
                "is_available": True,
            },
        )

    def mark_unavailable(self, platform: Platform, seen_external_ids: Iterable[str]) -> int:
        stale = Course.objects.filter(platform=platform, is_available=True).exclude(
            external_id__in=list(seen_external_ids)
        )
        return stale.update(is_available=False)

    @staticmethod
    def _category(name: str | None) -> Category | None:
        if not name:
            return None
        slug = slugify(name, allow_unicode=True) or "other"
        category, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
        return category
