"""Сценарій запуску збору даних однієї платформи."""

import logging

from django.utils import timezone

from apps.catalog.repositories import CourseRepository

from .models import ScrapeRun
from .ports import SourceProvider

logger = logging.getLogger(__name__)

EMPTY_SOURCE_ERROR = (
    "Джерело не повернуло жодного курсу. Можливо, змінилася структура сайту або він "
    "недоступний, тому курси платформи не позначено недоступними."
)


class UnknownPlatformError(LookupError):
    """Для ідентифікатора платформи не зареєстровано жодного збирача."""


class CollectionService:
    """Координує збирач, репозиторій і журнал запусків.

    Клас має одну відповідальність (запуск і облік одного збору). Збирачі та
    збереження курсів він отримує через абстракції ``SourceProvider`` і
    ``CourseRepository``, а журнал запусків веде напряму через модель ``ScrapeRun``.
    """

    def __init__(self, repository: CourseRepository, sources: SourceProvider) -> None:
        self._repository = repository
        self._sources = sources

    def run(self, platform_slug: str) -> ScrapeRun:
        """Запускає збір і повертає запис журналу.

        Невідомий ідентифікатор не потрапляє в журнал: ``ScrapeRun`` посилається на
        платформу, а створювати запис ``Platform`` для довільного рядка не можна.
        Замість цього виникає ``UnknownPlatformError``.
        """
        # Джерело визначаємо до ensure_platform, щоб не створювати зайвих платформ.
        if platform_slug not in self._sources.names():
            raise UnknownPlatformError(f"Невідома платформа: {platform_slug}")
        source = self._sources.get(platform_slug)
        platform = self._repository.ensure_platform(platform_slug)
        run = ScrapeRun.objects.create(platform=platform, status=ScrapeRun.Status.RUNNING)
        try:
            seen: list[str] = []
            for record in source.fetch():
                course, created = self._repository.upsert(platform, record)
                seen.append(course.external_id)
                if created:
                    run.courses_created += 1
                else:
                    run.courses_updated += 1
            if seen:
                run.courses_unavailable = self._repository.mark_unavailable(platform, seen)
                run.status = ScrapeRun.Status.SUCCESS
            else:
                # Порожня відповідь найчастіше означає збій збирача, а не зникнення
                # усіх курсів, тому каталог платформи не чіпаємо.
                logger.warning("Збирач платформи %s не повернув жодного курсу", platform_slug)
                run.status = ScrapeRun.Status.FAILED
                run.error = EMPTY_SOURCE_ERROR
        except Exception as exc:  # збій одного збирача не повинен зупиняти інші (НФВ-08)
            logger.exception("Збір даних платформи %s завершився помилкою", platform_slug)
            run.status = ScrapeRun.Status.FAILED
            run.error = str(exc)
        run.finished_at = timezone.now()
        run.save()
        return run
