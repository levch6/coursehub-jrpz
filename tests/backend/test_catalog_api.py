from decimal import Decimal

import pytest

from apps.catalog.models import Course

pytestmark = pytest.mark.django_db


def test_list_returns_paginated_courses(api, course):
    response = api.get("/api/courses/")
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == course.title


def test_detail_returns_course(api, course):
    response = api.get(f"/api/courses/{course.pk}/")
    assert response.status_code == 200
    assert response.data["platform"]["slug"] == "udemy"


def test_search_by_keyword(api, course):
    assert api.get("/api/courses/", {"q": "python"}).data["count"] == 1
    assert api.get("/api/courses/", {"q": "java"}).data["count"] == 0


def test_filter_by_platform_and_price(api, course, platform):
    Course.objects.create(
        platform=platform,
        external_id="2",
        title="Дорогий курс",
        url="https://example.com/2",
        price=Decimal("99.00"),
    )
    response = api.get("/api/courses/", {"platform": "udemy", "max_price": "50"})
    assert [c["title"] for c in response.data["results"]] == [course.title]


def test_ordering_by_price(api, course, platform):
    Course.objects.create(
        platform=platform,
        external_id="2",
        title="Дешевий курс",
        url="https://example.com/2",
        price=Decimal("1.00"),
    )
    response = api.get("/api/courses/", {"ordering": "price"})
    assert response.data["results"][0]["title"] == "Дешевий курс"


def test_hidden_courses_are_not_listed(api, course):
    course.is_hidden = True
    course.save()
    assert api.get("/api/courses/").data["count"] == 0
    assert api.get(f"/api/courses/{course.pk}/").status_code == 404


def test_categories_list(api, category):
    response = api.get("/api/categories/")
    assert response.status_code == 200
    assert response.data[0]["slug"] == "python"


def test_health_endpoint(api):
    response = api.get("/api/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_courses_without_rating_are_listed_last(api, course, platform):
    Course.objects.create(
        platform=platform, external_id="2", title="Без рейтингу", url="https://example.com/2"
    )
    default = api.get("/api/courses/").data["results"]
    ascending = api.get("/api/courses/", {"ordering": "rating"}).data["results"]
    assert default[-1]["title"] == "Без рейтингу"
    assert ascending[-1]["title"] == "Без рейтингу"
    assert "NULLS LAST" in str(Course.objects.all().query)
