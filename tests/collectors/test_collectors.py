import logging
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


def test_coursera_requests_offsets_not_page_numbers():
    fetcher = FakeFetcher([COURSERA_PAGE, COURSERA_PAGE, {"elements": []}])
    list(CourseraCollector(fetcher).fetch())
    assert [params["start"] for _, params in fetcher.calls] == [0, 50, 100]


def test_edx_collector_maps_fields():
    course = next(EdxCollector(FakeFetcher([EDX_PAGE])).fetch())
    assert course.external_id == "MITx+6.00x"
    assert course.level == "beginner"
    assert course.language == "en"


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


@pytest.mark.parametrize(
    "page",
    [
        {"results": [{**UDEMY_PAGE["results"][0], "title": None}]},
        {"results": [{**UDEMY_PAGE["results"][0], "avg_rating": 7}]},
        ["не словник"],
    ],
)
def test_unexpected_data_is_reported_as_parse_error(page):
    with pytest.raises(ParseError):
        list(UdemyCollector(FakeFetcher([page])).fetch())


def test_requests_fetcher_sends_its_own_user_agent_without_mutating_session():
    import requests

    from collectors.fetching import RequestsFetcher

    sent = {}

    class RecordingSession(requests.Session):
        def get(self, url, **kwargs):
            sent.update(kwargs)
            response = requests.Response()
            response.status_code = 200
            response._content = b"{}"
            return response

    session = RecordingSession()
    original_agent = session.headers["User-Agent"]
    assert RequestsFetcher(session=session, user_agent="CourseHubBot/test").get_json("u") == {}
    assert sent["headers"]["User-Agent"] == "CourseHubBot/test"
    assert session.headers["User-Agent"] == original_agent


def test_page_limit_is_logged_as_warning(caplog):
    class Endless:
        def get_json(self, url, params=None):
            return UDEMY_PAGE

    class Limited(UdemyCollector):
        max_pages = 2

    with caplog.at_level(logging.WARNING, logger="collectors.base"):
        list(Limited(Endless()).fetch())
    assert "udemy" in caplog.text
    assert "2" in caplog.text


def test_no_warning_when_pages_run_out(caplog):
    with caplog.at_level(logging.WARNING, logger="collectors.base"):
        list(UdemyCollector(FakeFetcher([UDEMY_PAGE, {"results": []}])).fetch())
    assert not caplog.records


def test_collector_without_platform_cannot_be_created():
    class Nameless(CourseCollector):
        def fetch(self):
            return iter(())

    with pytest.raises(TypeError, match="platform"):
        Nameless(FakeFetcher([]))


def _udemy_item(**overrides):
    return {**UDEMY_PAGE["results"][0], **overrides}


@pytest.mark.parametrize(
    ("raw_url", "expected"),
    [
        ("/course/python-bootcamp/", "https://www.udemy.com/course/python-bootcamp/"),
        ("course/python-bootcamp/", "https://www.udemy.com/course/python-bootcamp/"),
        ("https://www.udemy.com/course/abs/", "https://www.udemy.com/course/abs/"),
    ],
)
def test_udemy_builds_absolute_url(raw_url, expected):
    fetcher = FakeFetcher([{"results": [_udemy_item(url=raw_url)]}])
    assert next(UdemyCollector(fetcher).fetch()).url == expected


@pytest.mark.parametrize("raw_url", [None, "", "   "])
def test_udemy_rejects_missing_url(raw_url):
    fetcher = FakeFetcher([{"results": [_udemy_item(url=raw_url)]}])
    with pytest.raises(ParseError):
        list(UdemyCollector(fetcher).fetch())


@pytest.mark.parametrize(
    ("price", "currency", "amount"),
    [
        ("€19,99", "EUR", Decimal("19.99")),
        ("$19.99", "USD", Decimal("19.99")),
        (19.99, "USD", Decimal("19.99")),
        (None, "USD", None),
    ],
)
def test_udemy_takes_currency_from_price_symbol(price, currency, amount):
    fetcher = FakeFetcher([{"results": [_udemy_item(price=price)]}])
    course = next(UdemyCollector(fetcher).fetch())
    assert course.currency == currency
    assert course.price == amount


def test_explicit_nulls_become_empty_values():
    udemy = FakeFetcher([{"results": [_udemy_item(headline=None, category=None)]}])
    course = next(UdemyCollector(udemy).fetch())
    assert (course.description, course.category) == ("", None)

    raw = {**COURSERA_PAGE["elements"][0], "description": None, "domainTypes": None}
    course = next(CourseraCollector(FakeFetcher([{"elements": [raw]}])).fetch())
    assert (course.description, course.category) == ("", None)

    raw = {**EDX_PAGE["objects"][0], "short_description": None, "subject": None}
    course = next(EdxCollector(FakeFetcher([{"objects": [raw]}])).fetch())
    assert (course.description, course.category) == ("", None)


@pytest.mark.parametrize(
    ("subject", "expected"),
    [({"name": "Computer Science", "uuid": "x"}, "Computer Science"), ({}, None)],
)
def test_edx_subject_object_is_reduced_to_name(subject, expected):
    raw = {**EDX_PAGE["objects"][0], "subject": subject}
    course = next(EdxCollector(FakeFetcher([{"objects": [raw]}])).fetch())
    assert course.category == expected


def test_edx_numeric_key_is_converted_to_string():
    raw = {**EDX_PAGE["objects"][0], "key": 42}
    course = next(EdxCollector(FakeFetcher([{"objects": [raw]}])).fetch())
    assert course.external_id == "42"


@pytest.mark.parametrize("key", ["", "   "])
def test_edx_blank_key_is_parse_error(key):
    raw = {**EDX_PAGE["objects"][0], "key": key}
    with pytest.raises(ParseError):
        list(EdxCollector(FakeFetcher([{"objects": [raw]}])).fetch())
