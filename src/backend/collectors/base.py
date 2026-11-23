"""Базові класи збирачів.

``CourseCollector`` описує єдиний інтерфейс (принцип підстановки Лісков):
будь-який збирач можна використати замість іншого, бо всі повертають
``CourseDTO``. Нову платформу додають новим підкласом без змін наявного коду
(принцип відкритості/закритості, НФВ-05).
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, ClassVar

from .dto import CourseDTO
from .errors import ParseError
from .fetching import Fetcher

logger = logging.getLogger(__name__)


class CourseCollector(ABC):
    """Збирач курсів однієї платформи."""

    platform: ClassVar[str]

    def __init__(self, fetcher: Fetcher) -> None:
        if not getattr(type(self), "platform", ""):
            raise TypeError(f"{type(self).__name__} має задати атрибут класу platform")
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
    # True, якщо платформа приймає зсув від початку (0, 50, 100...), а не номер сторінки.
    offset_pagination: ClassVar[bool] = False

    @abstractmethod
    def extract_items(self, payload: Any) -> list[dict[str, Any]]:
        """Дістає список сирих елементів зі сторінки відповіді."""

    @abstractmethod
    def parse_item(self, raw: dict[str, Any]) -> CourseDTO:
        """Перетворює один сирий елемент на ``CourseDTO``."""

    def fetch(self) -> Iterator[CourseDTO]:
        """Обходить сторінки, доки платформа не поверне порожню сторінку.

        Якщо досягнуто ``max_pages``, а остання сторінка ще містила елементи,
        обхід зупиняється з попередженням у журналі: дані можуть бути неповними.
        Один некоректний елемент спричиняє ``ParseError`` і перериває збирання
        всієї платформи, щоб помилку формату не було пропущено непомітно.
        """
        for page in range(1, self.max_pages + 1):
            position = (page - 1) * self.page_size if self.offset_pagination else page
            payload = self._fetcher.get_json(
                self.endpoint, {self.page_param: position, self.page_size_param: self.page_size}
            )
            try:
                items = self.extract_items(payload)
            except (AttributeError, KeyError, TypeError, ValueError) as exc:
                raise ParseError(f"{self.platform}: неочікуваний формат сторінки: {exc}") from exc
            if not items:
                return
            for raw in items:
                yield self._parse(raw)
        logger.warning(
            "%s: досягнуто ліміту в %d сторінок, дані можуть бути неповними",
            self.platform,
            self.max_pages,
        )

    def _parse(self, raw: dict[str, Any]) -> CourseDTO:
        try:
            return self.parse_item(raw)
        except (AttributeError, KeyError, TypeError, ValueError, ArithmeticError) as exc:
            raise ParseError(f"{self.platform}: неочікуваний формат елемента: {exc}") from exc
