import pytest

from collectors import (
    CollectorRegistry,
    CourseCollector,
    UnknownPlatformError,
    build_default_registry,
)

from .conftest import FakeFetcher


class DummyCollector(CourseCollector):
    platform = "dummy"

    def fetch(self):
        return iter(())


def test_register_and_get():
    registry = CollectorRegistry()
    collector = DummyCollector(FakeFetcher([]))
    registry.register(collector)
    assert registry.get("dummy") is collector
    assert "dummy" in registry
    assert registry.names() == ["dummy"]


def test_duplicate_registration_is_rejected():
    registry = CollectorRegistry()
    registry.register(DummyCollector(FakeFetcher([])))
    with pytest.raises(ValueError, match="уже зареєстровано"):
        registry.register(DummyCollector(FakeFetcher([])))


def test_unknown_platform_raises_domain_error():
    with pytest.raises(UnknownPlatformError):
        CollectorRegistry().get("nope")


def test_default_registry_contains_three_platforms():
    registry = build_default_registry(FakeFetcher([]))
    assert registry.names() == ["coursera", "edx", "udemy"]


def test_new_platform_needs_no_changes_in_existing_code():
    """Принцип відкритості/закритості: нова платформа додається лише реєстрацією."""
    registry = build_default_registry(FakeFetcher([]))
    registry.register(DummyCollector(FakeFetcher([])))
    assert "dummy" in registry.names()
