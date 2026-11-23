"""Фікстури та допоміжні класи для тестів серверної частини."""

import os
from dataclasses import dataclass
from decimal import Decimal

import django
import pytest

# Налаштування Django підключаються тут, а не в pyproject.toml, щоб тести інших
# модулів (наприклад, збирачів) можна було запускати без серверного застосунку.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from rest_framework.test import APIClient  # noqa: E402

from apps.catalog.models import Category, Course, Platform  # noqa: E402

pytestmark = pytest.mark.django_db


@dataclass(frozen=True)
class FakeRecord:
    """Мінімальний запис про курс, що відповідає контракту ``CourseRecord``."""

    external_id: str
    title: str
    url: str = "https://example.com/course"
    description: str = ""
    category: str | None = None
    price: Decimal | None = Decimal("10.00")
    currency: str = "USD"
    rating: Decimal | None = Decimal("4.5")
    language: str = "en"
    level: str = "all"


class FakeSource:
    def __init__(self, platform: str, records: list[FakeRecord], error: Exception | None = None):
        self.platform = platform
        self._records = records
        self._error = error

    def fetch(self):
        if self._error:
            raise self._error
        yield from self._records


class FakeSources:
    """Реєстр джерел для тестів, що реалізує порт ``SourceProvider``."""

    def __init__(self, *sources: FakeSource):
        self._sources = {s.platform: s for s in sources}

    def names(self) -> list[str]:
        return sorted(self._sources)

    def get(self, name: str) -> FakeSource:
        return self._sources[name]


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user("user@example.com", "StrongPass123")


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_superuser("admin@example.com", "StrongPass123")


@pytest.fixture
def auth_api(api, user) -> APIClient:
    api.force_authenticate(user)
    return api


@pytest.fixture
def admin_api(admin_user) -> APIClient:
    client = APIClient()
    client.force_authenticate(admin_user)
    return client


@pytest.fixture
def platform(db) -> Platform:
    return Platform.objects.create(slug="udemy", name="Udemy")


@pytest.fixture
def category(db) -> Category:
    return Category.objects.create(slug="python", name="Python")


@pytest.fixture
def course(platform, category) -> Course:
    return Course.objects.create(
        platform=platform,
        category=category,
        external_id="1",
        title="Python для початківців",
        description="Основи мови програмування",
        url="https://example.com/python",
        price=Decimal("19.99"),
        rating=Decimal("4.70"),
        language="uk",
    )
