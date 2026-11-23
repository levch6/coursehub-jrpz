from decimal import Decimal

import pytest

from collectors import (
    CourseCollector,
    CourseDTO,
    ParseError,
    build_default_registry,
)
from collectors.coursera import CourseraCollector
from collectors.edx import EdxCollector
from collectors.udemy import UdemyCollector

from .conftest import FakeFetcher

UDEMY_PAGE = {
    "results": [
        {
            "id": 1,
            "title": "Python Bootcamp",
            "headline": "Learn Python",
            "url": "/course/python-bootcamp/",
            "price": "$19.99",
            "avg_rating": 4.6,
            "locale": "en_US",
            "instructional_level": "All Levels",
        }
    ]
}
COURSERA_PAGE = {
    "elements": [
        {
            "id": "abc",
            "name": "Machine Learning",
            "slug": "machine-learning",
            "description": "ML basics",
            "primaryLanguages": ["en"],
            "domainTypes": [{"domainId": "data-science"}],
            "level": "Intermediate",
        }
    ]
}
EDX_PAGE = {
    "objects": [
        {
            "key": "MITx+6.00x",
            "title": "Intro to CS",
            "short_description": "CS basics",
            "marketing_url": "https://www.edx.org/course/intro-cs",
            "language": "English",
            "level_type": "Introductory",
            "subject": "Computer Science",
        }
    ]
}


def test_udemy_collector_parses_page_and_stops_on_empty_page():
    fetcher = FakeFetcher([UDEMY_PAGE, {"results": []}])
    courses = list(UdemyCollector(fetcher).fetch())
    assert courses == [
        CourseDTO(
            external_id="1",
            title="Python Bootcamp",
            description="Learn Python",
            url="https://www.udemy.com/course/python-bootcamp/",
            price=Decimal("19.99"),
            rating=Decimal("4.6"),
            language="en",
            level="all",
        )
    ]
    assert len(fetcher.calls) == 2
    assert fetcher.calls[0][1] == {"page": 1, "page_size": 50}


def test_coursera_collector_uses_its_own_pagination_parameters():
    fetcher = FakeFetcher([COURSERA_PAGE])
    course = next(CourseraCollector(fetcher).fetch())
    assert course.url == "https://www.coursera.org/learn/machine-learning"
    assert course.category == "data-science"
    assert course.level == "intermediate"
    assert set(fetcher.calls[0][1]) == {"start", "limit"}


def test_edx_collector_maps_fields():
    course = next(EdxCollector(FakeFetcher([EDX_PAGE])).fetch())
    assert course.external_id == "MITx+6.00x"
    assert course.level == "beginner"
    assert course.language == "english"


def test_malformed_item_raises_parse_error():
    fetcher = FakeFetcher([{"results": [{"title": "Без ідентифікатора"}]}])
    with pytest.raises(ParseError):
        list(UdemyCollector(fetcher).fetch())


def test_page_limit_prevents_endless_loop():
    class Endless:
        def get_json(self, url, params=None):
            return UDEMY_PAGE

    class Limited(UdemyCollector):
        max_pages = 3

    assert len(list(Limited(Endless()).fetch())) == 3


@pytest.mark.parametrize("platform", ["udemy", "coursera", "edx"])
def test_every_registered_collector_honors_the_common_contract(platform):
    """Принцип підстановки Лісков: збирачі взаємозамінні за інтерфейсом."""
    pages = {"udemy": UDEMY_PAGE, "coursera": COURSERA_PAGE, "edx": EDX_PAGE}
    collector = build_default_registry(FakeFetcher([pages[platform]])).get(platform)
    assert isinstance(collector, CourseCollector)
    assert collector.platform == platform
    results = list(collector.fetch())
    assert results
    assert all(isinstance(item, CourseDTO) for item in results)
