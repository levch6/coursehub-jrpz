"""Порти (інтерфейси), через які застосунок працює зі збирачами.

Застосунок ``collection`` залежить лише від цих абстракцій, а конкретні збирачі
(пакет ``collectors``) їх реалізують. Так додавання нової платформи не вимагає
змін у цьому коді (принцип відкритості/закритості, НФВ-05).
"""

from collections.abc import Iterable
from typing import Protocol

from apps.catalog.records import CourseRecord


class CourseSource(Protocol):
    """Джерело курсів однієї платформи."""

    platform: str

    def fetch(self) -> Iterable[CourseRecord]: ...


class SourceProvider(Protocol):
    """Реєстр джерел: дає змогу отримати збирач за ідентифікатором платформи."""

    def names(self) -> list[str]: ...

    def get(self, name: str) -> CourseSource: ...
