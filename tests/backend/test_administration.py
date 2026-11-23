import pytest

from apps.collection import tasks as collection_tasks

from .conftest import FakeRecord, FakeSource, FakeSources

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def fake_sources(monkeypatch):
    sources = FakeSources(FakeSource("udemy", [FakeRecord("1", "A")]))
    monkeypatch.setattr("apps.administration.views.load_sources", lambda: sources)
    monkeypatch.setattr(collection_tasks, "load_sources", lambda: sources)
    return sources


def test_stats_forbidden_for_regular_user(auth_api):
    assert auth_api.get("/api/admin/stats/").status_code == 403


def test_stats_requires_authentication(api):
    assert api.get("/api/admin/stats/").status_code == 401


def test_stats_available_for_admin(admin_api, course):
    response = admin_api.get("/api/admin/stats/")
    assert response.status_code == 200
    assert response.data["courses"] == 1


def test_manual_collection_runs_and_is_logged(admin_api):
    response = admin_api.post("/api/admin/collection/udemy/run/")
    assert response.status_code == 202
    runs = admin_api.get("/api/admin/collection/runs/")
    assert runs.data["count"] == 1
    assert runs.data["results"][0]["status"] == "success"


def test_manual_collection_unknown_platform(admin_api):
    assert admin_api.post("/api/admin/collection/nope/run/").status_code == 404


def test_manual_collection_forbidden_for_user(auth_api):
    assert auth_api.post("/api/admin/collection/udemy/run/").status_code == 403


def test_admin_can_hide_course(admin_api, api, course):
    response = admin_api.patch(f"/api/admin/courses/{course.pk}/", {"is_hidden": True})
    assert response.status_code == 200
    assert api.get("/api/courses/").data["count"] == 0


def test_run_all_collections_queues_every_platform():
    names = collection_tasks.run_all_collections()
    assert names == ["udemy"]
