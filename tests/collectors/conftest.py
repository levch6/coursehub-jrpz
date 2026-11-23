"""Спільні допоміжні класи для тестів збирачів."""

from typing import Any

import pytest


class FakeFetcher:
    """Повертає заздалегідь підготовлені сторінки замість запитів у мережу."""

    def __init__(self, pages: list[Any]) -> None:
        self._pages = pages
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        self.calls.append((url, params))
        index = len(self.calls) - 1
        if index < len(self._pages):
            return self._pages[index]
        return {}


@pytest.fixture
def fake_fetcher_factory():
    return FakeFetcher
