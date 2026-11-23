import pytest

from apps.catalog.models import Course
from apps.catalog.repositories import DjangoCourseRepository
from apps.collection.models import ScrapeRun
from apps.collection.services import CollectionService

from .conftest import FakeRecord, FakeSource, FakeSources

pytestmark = pytest.mark.django_db


def make_service(*sources: FakeSource) -> CollectionService:
    return CollectionService(DjangoCourseRepository(), FakeSources(*sources))


def test_successful_run_saves_courses_and_logs_counts():
    source = FakeSource("udemy", [FakeRecord("1", "A"), FakeRecord("2", "B")])
    run = make_service(source).run("udemy")
    assert run.status == ScrapeRun.Status.SUCCESS
    assert (run.courses_created, run.courses_updated) == (2, 0)
    assert run.finished_at is not None
    assert Course.objects.count() == 2


def test_second_run_updates_and_marks_missing_courses_unavailable():
    make_service(FakeSource("udemy", [FakeRecord("1", "A"), FakeRecord("2", "B")])).run("udemy")
    run = make_service(FakeSource("udemy", [FakeRecord("1", "A new")])).run("udemy")
    assert (run.courses_created, run.courses_updated, run.courses_unavailable) == (0, 1, 1)
    assert not Course.objects.get(external_id="2").is_available


def test_failing_source_is_recorded_and_does_not_raise():
    source = FakeSource("edx", [], error=RuntimeError("сайт недоступний"))
    run = make_service(source).run("edx")
    assert run.status == ScrapeRun.Status.FAILED
    assert "недоступний" in run.error


def test_unknown_platform_is_recorded_as_failure():
    run = make_service().run("unknown")
    assert run.status == ScrapeRun.Status.FAILED
