"""Tests for DigestSkill."""

from unittest.mock import patch

import pytest

from src.skills.digest_skill import DigestSkill


@pytest.fixture
def valid_urls() -> list[str]:
    return ["https://example.com/rss", "http://blog.test/feed"]


@pytest.fixture
def mock_feed_entry():
    """Returns a feedparser-like entry object."""
    entry = {
        "title": "Test Article",
        "link": "https://example.com/article/1",
        "summary": "Short description of the article.",
        "published": "Mon, 10 Mar 2026 10:00:00 GMT",
    }
    return type("Entry", (), {"get": entry.get})()


@pytest.fixture
def mock_parsed_feed(mock_feed_entry):
    """Returns a feedparser-like parsed feed result."""
    return type("Feed", (), {"bozo": False, "entries": [mock_feed_entry]})()


# --- validate_urls ---


def test_validate_urls_with_valid_urls_returns_empty(valid_urls: list[str]) -> None:
    skill = DigestSkill(urls=valid_urls)
    assert skill.validate_urls() == []


def test_validate_urls_with_invalid_urls_returns_bad_ones() -> None:
    urls = ["https://good.com/feed", "ftp://bad.com/rss", "not-a-url"]
    skill = DigestSkill(urls=urls)
    invalid = skill.validate_urls()
    assert "ftp://bad.com/rss" in invalid
    assert "not-a-url" in invalid
    assert "https://good.com/feed" not in invalid


# --- fetch_feed ---


def test_fetch_feed_with_valid_feed_returns_entries(mock_parsed_feed) -> None:
    skill = DigestSkill(urls=[])
    with patch("src.skills.digest_skill.feedparser.parse", return_value=mock_parsed_feed):
        entries = skill.fetch_feed("https://example.com/rss")
    assert len(entries) == 1
    assert entries[0]["title"] == "Test Article"
    assert entries[0]["link"] == "https://example.com/article/1"


def test_fetch_feed_with_invalid_url_returns_empty() -> None:
    bozo_feed = type("Feed", (), {
        "bozo": True,
        "bozo_exception": Exception("not well-formed"),
        "entries": [],
    })()
    skill = DigestSkill(urls=[])
    with patch("src.skills.digest_skill.feedparser.parse", return_value=bozo_feed):
        entries = skill.fetch_feed("https://broken.test/rss")
    assert entries == []
    assert len(skill._errors) == 1


def test_fetch_feed_with_network_error_returns_empty() -> None:
    skill = DigestSkill(urls=[])
    with patch(
        "src.skills.digest_skill.feedparser.parse",
        side_effect=OSError("connection refused"),
    ):
        entries = skill.fetch_feed("https://down.test/rss")
    assert entries == []
    assert len(skill._errors) == 1


# --- generate_digest ---


def test_generate_digest_empty_urls_returns_no_valid() -> None:
    skill = DigestSkill(urls=[])
    result = skill.generate_digest()
    assert result == "No valid URLs provided."


def test_generate_digest_formats_output(mock_parsed_feed) -> None:
    skill = DigestSkill(urls=["https://example.com/rss"])
    with patch("src.skills.digest_skill.feedparser.parse", return_value=mock_parsed_feed):
        result = skill.generate_digest()
    assert "== example.com ==" in result
    assert "Test Article" in result
    assert "https://example.com/article/1" in result
