"""Базові класи збирачів.

``CourseCollector`` описує єдиний інтерфейс (принцип підстановки Лісков):
будь-який збирач можна використати замість іншого, бо всі повертають
``CourseDTO``. Нову платформу додають новим підкласом без змін наявного коду
(принцип відкритості/закритості, НФВ-05).
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, ClassVar

from .dto import CourseDTO
from .errors import ParseError
from .fetching import Fetcher


class CourseCollector(ABC):
    """Збирач курсів однієї платформи."""

    platform: ClassVar[str]

    def __init__(self, fetcher: Fetcher) -> None:
        self._fetcher = fetcher

    @abstractmethod
    def fetch(self) -> Iterator[CourseDTO]:
        """Повертає всі доступні курси платформи у форматі ``CourseDTO``."""


class PagedJsonCollector(CourseCollector):
    """Шаблон для платформ, що віддають курси сторінками у форматі JSON.

    Підклас задає адресу та параметри пагінації й описує, як витягти список
    елементів із відповіді та як перетворити один елемент на ``CourseDTO``.
    """

    endpoint: ClassVar[str]
    page_param: ClassVar[str] = "page"
    page_size_param: ClassVar[str] = "page_size"
    page_size: ClassVar[int] = 50
    max_pages: ClassVar[int] = 100  # захист від нескінченного циклу

    @abstractmethod
    def extract_items(self, payload: Any) -> list[dict[str, Any]]:
        """Дістає список сирих елементів зі сторінки відповіді."""

    @abstractmethod
    def parse_item(self, raw: dict[str, Any]) -> CourseDTO:
        """Перетворює один сирий елемент на ``CourseDTO``."""

    def fetch(self) -> Iterator[CourseDTO]:
        for page in range(1, self.max_pages + 1):
            payload = self._fetcher.get_json(
                self.endpoint, {self.page_param: page, self.page_size_param: self.page_size}
            )
            items = self.extract_items(payload)
            if not items:
                return
            for raw in items:
                try:
                    yield self.parse_item(raw)
                except (KeyError, TypeError, ValueError) as exc:
                    message = f"{self.platform}: неочікуваний формат елемента: {exc}"
                    raise ParseError(message) from exc
