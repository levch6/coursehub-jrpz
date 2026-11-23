from decimal import Decimal

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


def test_upsert_keeps_admin_edits_but_updates_collected_fields(repo):
    platform = repo.ensure_platform("udemy")
    course, _ = repo.upsert(platform, FakeRecord("1", "Original", category="Web"))
    Course.objects.filter(pk=course.pk).update(
        title="Виправлена назва", description="Опис адміністратора", is_edited=True
    )
    record = FakeRecord("1", "Original", category="Data", price=Decimal("5.00"))
    course, created = repo.upsert(platform, record)
    assert not created
    assert course.title == "Виправлена назва"
    assert course.description == "Опис адміністратора"
    assert course.category.slug == "web"
    assert course.price == Decimal("5.00")


def test_long_category_name_gets_slug_within_limit(repo):
    platform = repo.ensure_platform("udemy")
    prefix = "Програмування та розробка програмного забезпечення для початківців "
    first, _ = repo.upsert(platform, FakeRecord("1", "A", category=prefix + "частина перша"))
    second, _ = repo.upsert(platform, FakeRecord("2", "B", category=prefix + "частина друга"))
    assert len(first.category.slug) <= 50
    assert first.category.slug != second.category.slug
    again, _ = repo.upsert(platform, FakeRecord("3", "C", category=prefix + "частина перша"))
    assert again.category_id == first.category_id


def test_long_title_and_external_id_are_truncated(repo):
    platform = repo.ensure_platform("udemy")
    course, _ = repo.upsert(platform, FakeRecord("x" * 300, "Назва " * 100))
    assert len(course.external_id) == 200
    assert len(course.title) == 500
