"""Реєстр збирачів: пошук збирача за ідентифікатором платформи.

Клас реалізує порт ``SourceProvider`` із застосунку ``collection``, тому
серверна частина працює з ним, не знаючи про конкретні платформи.
"""

from collections.abc import Iterator

from .base import CourseCollector
from .coursera import CourseraCollector
from .edx import EdxCollector
from .errors import UnknownPlatformError
from .fetching import Fetcher, RequestsFetcher
from .udemy import UdemyCollector


class CollectorRegistry:
    def __init__(self) -> None:
        self._collectors: dict[str, CourseCollector] = {}

    def register(self, collector: CourseCollector) -> None:
        platform = collector.platform
        if platform in self._collectors:
            raise ValueError(f"Збирач платформи {platform!r} уже зареєстровано")
        self._collectors[platform] = collector

    def get(self, name: str) -> CourseCollector:
        try:
            return self._collectors[name]
        except KeyError:
            raise UnknownPlatformError(f"Невідома платформа: {name!r}") from None

    def names(self) -> list[str]:
        return sorted(self._collectors)

    def __contains__(self, name: str) -> bool:
        return name in self._collectors

    def __iter__(self) -> Iterator[CourseCollector]:
        return iter(self._collectors.values())


def build_default_registry(fetcher: Fetcher | None = None) -> CollectorRegistry:
    """Створює реєстр зі збирачами Udemy, Coursera та edX."""
    fetcher = fetcher or RequestsFetcher()
    registry = CollectorRegistry()
    for collector_class in (UdemyCollector, CourseraCollector, EdxCollector):
        registry.register(collector_class(fetcher))
    return registry
