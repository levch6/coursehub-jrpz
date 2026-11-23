import pytest

from apps.catalog.models import Course
from apps.catalog.normalization import make_fingerprint
from apps.catalog.repositories import DjangoCourseRepository

from .conftest import FakeRecord

pytestmark = pytest.mark.django_db


@pytest.fixture
def repo() -> DjangoCourseRepository:
    return DjangoCourseRepository()


def test_ensure_platform_is_idempotent(repo):
    first = repo.ensure_platform("coursera")
    second = repo.ensure_platform("coursera")
    assert first.pk == second.pk
    assert first.name == "Coursera"


def test_upsert_creates_then_updates_without_duplicates(repo):
    platform = repo.ensure_platform("udemy")
    course, created = repo.upsert(platform, FakeRecord("42", "Django", category="Web"))
    assert created
    course, created = repo.upsert(platform, FakeRecord("42", "Django 2", category="Web"))
    assert not created
    assert Course.objects.count() == 1
    assert course.title == "Django 2"
    assert course.category.slug == "web"
    assert course.fingerprint == make_fingerprint("Django 2", "en")


def test_same_external_id_on_other_platform_is_separate_course(repo):
    udemy = repo.ensure_platform("udemy")
    edx = repo.ensure_platform("edx")
    repo.upsert(udemy, FakeRecord("1", "A"))
    repo.upsert(edx, FakeRecord("1", "A"))
    assert Course.objects.count() == 2


def test_mark_unavailable_only_for_unseen_courses(repo):
    platform = repo.ensure_platform("udemy")
    repo.upsert(platform, FakeRecord("1", "Keep"))
    repo.upsert(platform, FakeRecord("2", "Drop"))
    changed = repo.mark_unavailable(platform, ["1"])
    assert changed == 1
    assert Course.objects.get(external_id="1").is_available
    assert not Course.objects.get(external_id="2").is_available
