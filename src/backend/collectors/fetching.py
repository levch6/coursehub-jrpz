"""Отримання даних із мережі.

Збирачі залежать від абстракції ``Fetcher``, а не від бібліотеки ``requests``
(принцип інверсії залежностей), тому в тестах мережа не потрібна.

Перед підключенням реальних адрес необхідно перевірити ``robots.txt`` і умови
використання кожної платформи та обмежити частоту запитів (НФВ-21).
"""

from typing import Any, Protocol

import requests

from .errors import FetchError


class Fetcher(Protocol):
    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any: ...


class RequestsFetcher:
    """Реалізація ``Fetcher`` поверх HTTP-сесії з таймаутом і ідентифікацією бота."""

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: float = 10.0,
        user_agent: str = "CourseHubBot/0.1 (навчальний проєкт)",
    ) -> None:
        self._session = session or requests.Session()
        self._session.headers.setdefault("User-Agent", user_agent)
        self._timeout = timeout

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        try:
            response = self._session.get(url, params=params, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            raise FetchError(f"Не вдалося отримати {url}: {exc}") from exc
