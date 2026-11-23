"""Сценарій запуску збору даних однієї платформи."""

import logging

from django.utils import timezone

from apps.catalog.repositories import CourseRepository

from .models import ScrapeRun
from .ports import SourceProvider

logger = logging.getLogger(__name__)


class CollectionService:
    """Координує збирач, репозиторій і журнал запусків.

    Клас має одну відповідальність (запуск і облік одного збору) і залежить
    від абстракцій ``CourseRepository`` та ``SourceProvider``.
    """

    def __init__(self, repository: CourseRepository, sources: SourceProvider) -> None:
        self._repository = repository
        self._sources = sources

    def run(self, platform_slug: str) -> ScrapeRun:
        platform = self._repository.ensure_platform(platform_slug)
        run = ScrapeRun.objects.create(platform=platform, status=ScrapeRun.Status.RUNNING)
        try:
            source = self._sources.get(platform_slug)
            seen: list[str] = []
            for record in source.fetch():
                _course, created = self._repository.upsert(platform, record)
                seen.append(record.external_id)
                if created:
                    run.courses_created += 1
                else:
                    run.courses_updated += 1
            run.courses_unavailable = self._repository.mark_unavailable(platform, seen)
            run.status = ScrapeRun.Status.SUCCESS
        except Exception as exc:  # збій одного збирача не повинен зупиняти інші (НФВ-08)
            logger.exception("Збір даних платформи %s завершився помилкою", platform_slug)
            run.status = ScrapeRun.Status.FAILED
            run.error = str(exc)
        run.finished_at = timezone.now()
        run.save()
        return run
