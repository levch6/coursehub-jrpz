"""Celery-задачі збору даних (ФВ-03, ФВ-04)."""

from celery import shared_task

from apps.catalog.repositories import DjangoCourseRepository

from .providers import load_sources
from .services import CollectionService


@shared_task
def run_collection(platform_slug: str) -> int:
    """Запускає збір для однієї платформи та повертає ідентифікатор запису в журналі."""
    service = CollectionService(DjangoCourseRepository(), load_sources())
    return service.run(platform_slug).pk


@shared_task
def run_all_collections() -> list[str]:
    """Ставить у чергу окрему задачу для кожної зареєстрованої платформи."""
    names = load_sources().names()
    for name in names:
        run_collection.delay(name)
    return names
