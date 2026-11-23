"""Репозиторій курсів.

Абстракція ``CourseRepository`` відокремлює бізнес-логіку збору даних від ORM
(принцип інверсії залежностей). У тестах її замінює проста реалізація.
"""

import hashlib
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
        external_id = _truncate(record.external_id, Course, "external_id")
        title = _truncate(record.title, Course, "title")
        collected = {
            "url": record.url,
            "price": record.price,
            "currency": record.currency,
            "rating": record.rating,
            "language": record.language,
            "level": record.level,
            "is_available": True,
        }
        editable = {
            "title": title,
            "description": record.description,
            "category": self._category(record.category),
            "fingerprint": make_fingerprint(title, record.language),
        }
        # Поля, відредаговані адміністратором (ФВ-23), збір не перезаписує.
        edited = Course.objects.filter(
            platform=platform, external_id=external_id, is_edited=True
        ).exists()
        return Course.objects.update_or_create(
            platform=platform,
            external_id=external_id,
            defaults=collected if edited else {**collected, **editable},
            create_defaults={**collected, **editable},
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
        limit = Category._meta.get_field("slug").max_length
        if len(slug) > limit:
            # Короткий хеш повної назви відрізняє довгі назви зі спільним початком.
            digest = hashlib.sha1(name.encode(), usedforsecurity=False).hexdigest()[:8]
            slug = f"{slug[: limit - len(digest) - 1].rstrip('-')}-{digest}"
        category, _ = Category.objects.get_or_create(
            slug=slug, defaults={"name": _truncate(name, Category, "name")}
        )
        return category


def _truncate(value: str, model, field: str) -> str:
    """Обрізає рядок до max_length поля, щоб задовге значення не зупинило збір."""
    return value[: model._meta.get_field(field).max_length]
