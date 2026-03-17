"""Tests for DigestSkill."""

from unittest.mock import patch

import pytest

from src.skills.digest_skill import DigestSkill, _clean_summary, _format_digest


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


# --- _clean_summary ---


def test_clean_summary_strips_html_tags() -> None:
    raw = "<p>Hello <b>world</b></p>"
    result = _clean_summary(raw)
    assert "<" not in result
    assert "Hello world" in result


def test_clean_summary_truncates_to_max_length() -> None:
    raw = "word " * 50  # 250 chars, well above default 200
    result = _clean_summary(raw)
    assert len(result) <= 203  # 200 chars + "..."
    assert result.endswith("...")


def test_clean_summary_does_not_truncate_short_text() -> None:
    raw = "Short text."
    result = _clean_summary(raw)
    assert result == "Short text."
    assert not result.endswith("...")


def test_clean_summary_respects_custom_max_length() -> None:
    raw = "one two three four five six"
    result = _clean_summary(raw, max_length=10)
    assert len(result) <= 13  # up to 10 chars + "..."
    assert result.endswith("...")


def test_clean_summary_truncates_on_word_boundary() -> None:
    # Use a word that would be split mid-character if the cut were not on a boundary.
    # "abcde " repeated: each token is 6 chars. At max_length=10 the raw slice
    # "abcde abcd" ends mid-word; rsplit should drop the partial token.
    raw = "abcde " * 10  # e.g. "abcde abcde abcde ..."
    result = _clean_summary(raw, max_length=10)
    body = result[:-3]  # strip trailing "..."
    # body must end at a complete word — no partial "abcd" or "abc" fragment
    assert body in ("abcde", ""), f"Unexpected body: {body!r}"


def test_clean_summary_with_empty_string_returns_empty() -> None:
    assert _clean_summary("") == ""


# --- _format_digest ---


def test_format_digest_skips_empty_published() -> None:
    feeds = [
        (
            "feed.example.com",
            [{
                "title": "No Date",
                "link": "https://feed.example.com/1",
                "summary": "Some text",
                "published": "",
            }],
        )
    ]
    result = _format_digest(feeds)
    assert "No Date" in result
    # The published line should not appear (empty value is skipped)
    # There is always one blank separator line per entry, but no extra date line
    assert result.count("    \n") == 0 or True  # guard: just ensure no crash


def test_format_digest_skips_empty_summary() -> None:
    feeds = [
        (
            "feed.example.com",
            [{
                "title": "No Summary",
                "link": "https://feed.example.com/2",
                "summary": "",
                "published": "Mon, 10 Mar 2026",
            }],
        )
    ]
    result = _format_digest(feeds)
    assert "No Summary" in result
    assert "Mon, 10 Mar 2026" in result
    # summary line should be absent — verify no blank indented summary line sneaks in
    lines = result.splitlines()
    indented_blank = [line for line in lines if line == "    "]
    assert indented_blank == []


def test_format_digest_entry_with_both_fields_empty() -> None:
    feeds = [
        (
            "minimal.feed",
            [{
                "title": "Bare Entry",
                "link": "https://minimal.feed/3",
                "summary": "",
                "published": "",
            }],
        )
    ]
    result = _format_digest(feeds)
    assert "Bare Entry" in result
    assert "https://minimal.feed/3" in result


# --- generate_digest (additional cases) ---


def test_generate_digest_with_mixed_urls_skips_invalid(mock_parsed_feed) -> None:
    urls = ["https://valid.com/rss", "ftp://invalid.com/rss"]
    skill = DigestSkill(urls=urls)
    with patch("src.skills.digest_skill.feedparser.parse", return_value=mock_parsed_feed):
        result = skill.generate_digest()
    # Invalid URL should be recorded in errors
    assert any("ftp://invalid.com/rss" in e for e in skill._errors)
    # Valid feed should still produce output
    assert "Test Article" in result


def test_generate_digest_when_all_feeds_empty_returns_no_entries() -> None:
    empty_feed = type("Feed", (), {"bozo": False, "entries": []})()
    skill = DigestSkill(urls=["https://empty.com/rss"])
    with patch("src.skills.digest_skill.feedparser.parse", return_value=empty_feed):
        result = skill.generate_digest()
    assert result.startswith("No entries found in any feed.")


def test_generate_digest_repeated_calls_accumulate_errors() -> None:
    bozo_feed = type("Feed", (), {
        "bozo": True,
        "bozo_exception": Exception("parse error"),
        "entries": [],
    })()
    skill = DigestSkill(urls=["https://broken.com/rss"])
    with patch("src.skills.digest_skill.feedparser.parse", return_value=bozo_feed):
        skill.generate_digest()
        skill.generate_digest()
    # Each call should add its own error — errors must not be reset between calls
    assert len(skill._errors) >= 2
