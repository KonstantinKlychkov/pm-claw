"""Tests for BriefingSkill and _format_briefing_text helper."""

from __future__ import annotations

import re
from unittest.mock import patch

import pytest

from src.skills.briefing_skill import BriefingSkill, _format_briefing_text
from src.skills.digest_skill import DigestSkill
from src.skills.idea_generator import IdeaGeneratorSkill


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_skill() -> BriefingSkill:
    """BriefingSkill with realistic feed URLs, topic, and action items."""
    return BriefingSkill(
        feed_urls=["https://example.com/rss", "https://blog.test/feed"],
        idea_topic="remote collaboration tools",
        action_items=["Review Q2 roadmap", "Schedule user interviews"],
    )


@pytest.fixture
def mock_digest_text() -> str:
    return "== example.com ==\n  - Test Article\n    https://example.com/article/1"


@pytest.fixture
def mock_ideas_text() -> str:
    return "=== SCAMPER Ideas: remote collaboration tools ===\n\n[Substitute]\n  Some prompt"


# ---------------------------------------------------------------------------
# collect_news — return value
# ---------------------------------------------------------------------------


def test_collect_news_returns_digest_text(
    valid_skill: BriefingSkill, mock_digest_text: str
) -> None:
    with patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text):
        result = valid_skill.collect_news()
    assert result == mock_digest_text


# ---------------------------------------------------------------------------
# collect_news — caching
# ---------------------------------------------------------------------------


def test_collect_news_stores_result_in_sections(
    valid_skill: BriefingSkill, mock_digest_text: str
) -> None:
    with patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text):
        valid_skill.collect_news()
    assert valid_skill._sections["news"] == mock_digest_text


# ---------------------------------------------------------------------------
# collect_news — error propagation
# ---------------------------------------------------------------------------


def test_collect_news_collects_errors_from_digest_skill(valid_skill: BriefingSkill) -> None:
    def fake_generate_digest(self: DigestSkill) -> str:
        self._errors.append("Error fetching https://example.com/rss: timeout")
        return "partial digest"

    with patch.object(DigestSkill, "generate_digest", fake_generate_digest):
        valid_skill.collect_news()

    assert any("timeout" in e for e in valid_skill._errors)


# ---------------------------------------------------------------------------
# collect_ideas — return value
# ---------------------------------------------------------------------------


def test_collect_ideas_returns_report_text(
    valid_skill: BriefingSkill, mock_ideas_text: str
) -> None:
    with patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text):
        result = valid_skill.collect_ideas()
    assert result == mock_ideas_text


# ---------------------------------------------------------------------------
# collect_ideas — caching
# ---------------------------------------------------------------------------


def test_collect_ideas_stores_result_in_sections(
    valid_skill: BriefingSkill, mock_ideas_text: str
) -> None:
    with patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text):
        valid_skill.collect_ideas()
    assert valid_skill._sections["ideas"] == mock_ideas_text


# ---------------------------------------------------------------------------
# collect_ideas — error propagation
# ---------------------------------------------------------------------------


def test_collect_ideas_collects_errors_from_idea_generator_skill(
    valid_skill: BriefingSkill,
) -> None:
    def fake_format_report(self: IdeaGeneratorSkill) -> str:
        self._errors.append("Topic cannot be empty.")
        return "No ideas generated."

    with patch.object(IdeaGeneratorSkill, "format_report", fake_format_report):
        valid_skill.collect_ideas()

    assert any("Topic cannot be empty" in e for e in valid_skill._errors)


# ---------------------------------------------------------------------------
# generate_briefing — happy path
# ---------------------------------------------------------------------------


def test_generate_briefing_happy_path_contains_header(
    valid_skill: BriefingSkill, mock_digest_text: str, mock_ideas_text: str
) -> None:
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = valid_skill.generate_briefing()
    assert "=== PM Daily Briefing ===" in result


def test_generate_briefing_happy_path_contains_date(
    valid_skill: BriefingSkill, mock_digest_text: str, mock_ideas_text: str
) -> None:
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = valid_skill.generate_briefing()
    assert "Date:" in result


def test_generate_briefing_happy_path_contains_news_section(
    valid_skill: BriefingSkill, mock_digest_text: str, mock_ideas_text: str
) -> None:
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = valid_skill.generate_briefing()
    assert "--- News Digest ---" in result
    assert mock_digest_text in result


def test_generate_briefing_happy_path_contains_ideas_section(
    valid_skill: BriefingSkill, mock_digest_text: str, mock_ideas_text: str
) -> None:
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = valid_skill.generate_briefing()
    assert "--- Ideas ---" in result
    assert mock_ideas_text in result


def test_generate_briefing_happy_path_contains_action_items_section(
    valid_skill: BriefingSkill, mock_digest_text: str, mock_ideas_text: str
) -> None:
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = valid_skill.generate_briefing()
    assert "--- Action Items ---" in result
    assert "- Review Q2 roadmap" in result
    assert "- Schedule user interviews" in result


# ---------------------------------------------------------------------------
# generate_briefing — empty feed_urls
# ---------------------------------------------------------------------------


def test_generate_briefing_with_empty_feed_urls_news_section_shows_fallback(
    mock_ideas_text: str,
) -> None:
    skill = BriefingSkill(feed_urls=[], idea_topic="remote collaboration tools")
    with patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text):
        result = skill.generate_briefing()
    assert "No news available." in result or "No valid URLs" in result


# ---------------------------------------------------------------------------
# generate_briefing — empty idea_topic
# ---------------------------------------------------------------------------


def test_generate_briefing_with_empty_idea_topic_ideas_section_handles_gracefully(
    mock_digest_text: str,
) -> None:
    skill = BriefingSkill(feed_urls=["https://example.com/rss"], idea_topic="")
    with patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text):
        result = skill.generate_briefing()
    # IdeaGeneratorSkill returns an error message for empty topic — section must not crash
    assert "--- Ideas ---" in result


# ---------------------------------------------------------------------------
# generate_briefing — action items
# ---------------------------------------------------------------------------


def test_generate_briefing_with_action_items_lists_them(
    mock_digest_text: str, mock_ideas_text: str
) -> None:
    skill = BriefingSkill(
        feed_urls=["https://example.com/rss"],
        idea_topic="topic",
        action_items=["Write spec", "Talk to sales"],
    )
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = skill.generate_briefing()
    assert "- Write spec" in result
    assert "- Talk to sales" in result


def test_generate_briefing_without_action_items_says_no_action_items(
    mock_digest_text: str, mock_ideas_text: str
) -> None:
    skill = BriefingSkill(
        feed_urls=["https://example.com/rss"],
        idea_topic="topic",
    )
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = skill.generate_briefing()
    assert "No action items." in result


# ---------------------------------------------------------------------------
# generate_briefing — errors section
# ---------------------------------------------------------------------------


def test_generate_briefing_includes_errors_section_when_errors_exist(
    mock_ideas_text: str,
) -> None:
    skill = BriefingSkill(feed_urls=["https://example.com/rss"], idea_topic="topic")

    def fake_generate_digest(self: DigestSkill) -> str:
        self._errors.append("Error fetching https://example.com/rss: timeout")
        return "partial digest"

    with (
        patch.object(DigestSkill, "generate_digest", fake_generate_digest),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = skill.generate_briefing()

    assert "--- Errors ---" in result
    assert "timeout" in result


def test_generate_briefing_omits_errors_section_when_no_errors(
    valid_skill: BriefingSkill, mock_digest_text: str, mock_ideas_text: str
) -> None:
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = valid_skill.generate_briefing()
    assert "--- Errors ---" not in result


# ---------------------------------------------------------------------------
# format_briefing — auto-generate when cache empty
# ---------------------------------------------------------------------------


def test_format_briefing_auto_generates_when_sections_empty(
    valid_skill: BriefingSkill, mock_digest_text: str, mock_ideas_text: str
) -> None:
    assert valid_skill._sections == {}
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = valid_skill.format_briefing()
    assert "=== PM Daily Briefing ===" in result
    assert valid_skill._sections != {}


# ---------------------------------------------------------------------------
# format_briefing — uses cache when available
# ---------------------------------------------------------------------------


def test_format_briefing_uses_cached_sections_when_available(
    valid_skill: BriefingSkill, mock_digest_text: str, mock_ideas_text: str
) -> None:
    # Pre-populate cache directly
    valid_skill._sections["news"] = mock_digest_text
    valid_skill._sections["ideas"] = mock_ideas_text

    # generate_digest and format_report must NOT be called
    with (
        patch.object(DigestSkill, "generate_digest", side_effect=AssertionError("should not call")),
        patch.object(
            IdeaGeneratorSkill, "format_report", side_effect=AssertionError("should not call")
        ),
    ):
        result = valid_skill.format_briefing()

    assert mock_digest_text in result
    assert mock_ideas_text in result


# ---------------------------------------------------------------------------
# _format_briefing_text helper — structure
# ---------------------------------------------------------------------------


def test_format_briefing_text_contains_briefing_header() -> None:
    result = _format_briefing_text("2026-03-14", "news", "ideas", [], [])
    assert "=== PM Daily Briefing ===" in result


def test_format_briefing_text_contains_provided_date() -> None:
    result = _format_briefing_text("2026-03-14", "news", "ideas", [], [])
    assert "Date: 2026-03-14" in result


def test_format_briefing_text_contains_news_content() -> None:
    result = _format_briefing_text("2026-03-14", "some news", "ideas", [], [])
    assert "some news" in result


def test_format_briefing_text_contains_ideas_content() -> None:
    result = _format_briefing_text("2026-03-14", "news", "great ideas", [], [])
    assert "great ideas" in result


def test_format_briefing_text_shows_fallback_when_news_empty() -> None:
    result = _format_briefing_text("2026-03-14", "", "ideas", [], [])
    assert "No news available." in result


def test_format_briefing_text_shows_fallback_when_ideas_empty() -> None:
    result = _format_briefing_text("2026-03-14", "news", "", [], [])
    assert "No ideas available." in result


def test_format_briefing_text_lists_action_items_with_dash() -> None:
    result = _format_briefing_text("2026-03-14", "news", "ideas", ["Task A", "Task B"], [])
    assert "- Task A" in result
    assert "- Task B" in result


def test_format_briefing_text_says_no_action_items_when_list_empty() -> None:
    result = _format_briefing_text("2026-03-14", "news", "ideas", [], [])
    assert "No action items." in result


def test_format_briefing_text_includes_errors_when_present() -> None:
    result = _format_briefing_text("2026-03-14", "news", "ideas", [], ["err1", "err2"])
    assert "--- Errors ---" in result
    assert "err1" in result
    assert "err2" in result


def test_format_briefing_text_omits_errors_section_when_no_errors() -> None:
    result = _format_briefing_text("2026-03-14", "news", "ideas", [], [])
    assert "--- Errors ---" not in result


def test_format_briefing_text_returns_string() -> None:
    result = _format_briefing_text("2026-03-14", "news", "ideas", [], [])
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# collect_news — error accumulation across repeated calls
# ---------------------------------------------------------------------------


def test_collect_news_called_twice_accumulates_errors(valid_skill: BriefingSkill) -> None:
    def fake_generate_digest(self: DigestSkill) -> str:
        self._errors.append("Error fetching feed: timeout")
        return "partial digest"

    with patch.object(DigestSkill, "generate_digest", fake_generate_digest):
        valid_skill.collect_news()
        valid_skill.collect_news()

    assert len([e for e in valid_skill._errors if "timeout" in e]) == 2


# ---------------------------------------------------------------------------
# collect_ideas — error accumulation across repeated calls
# ---------------------------------------------------------------------------


def test_collect_ideas_called_twice_accumulates_errors(valid_skill: BriefingSkill) -> None:
    def fake_format_report(self: IdeaGeneratorSkill) -> str:
        self._errors.append("Topic cannot be empty.")
        return "No ideas generated."

    with patch.object(IdeaGeneratorSkill, "format_report", fake_format_report):
        valid_skill.collect_ideas()
        valid_skill.collect_ideas()

    assert len([e for e in valid_skill._errors if "Topic cannot be empty" in e]) == 2


# ---------------------------------------------------------------------------
# generate_briefing — date format is ISO YYYY-MM-DD
# ---------------------------------------------------------------------------


def test_generate_briefing_date_is_iso_format(
    valid_skill: BriefingSkill, mock_digest_text: str, mock_ideas_text: str
) -> None:
    with (
        patch.object(DigestSkill, "generate_digest", return_value=mock_digest_text),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=mock_ideas_text),
    ):
        result = valid_skill.generate_briefing()
    assert re.search(r"Date: \d{4}-\d{2}-\d{2}", result)


# ---------------------------------------------------------------------------
# _format_briefing_text — both news and ideas empty
# ---------------------------------------------------------------------------


def test_format_briefing_text_shows_both_fallbacks_when_news_and_ideas_empty() -> None:
    result = _format_briefing_text("2026-03-14", "", "", [], [])
    assert "No news available." in result
    assert "No ideas available." in result


# ---------------------------------------------------------------------------
# format_briefing — partial cache (only "news" key)
# ---------------------------------------------------------------------------


def test_format_briefing_with_partial_cache_uses_cached_news(
    valid_skill: BriefingSkill, mock_digest_text: str
) -> None:
    valid_skill._sections["news"] = mock_digest_text
    # format_briefing takes the cached branch when _sections is non-empty,
    # so generate_digest / format_report must NOT be called.
    with (
        patch.object(
            DigestSkill, "generate_digest", side_effect=AssertionError("should not call")
        ),
        patch.object(
            IdeaGeneratorSkill, "format_report", side_effect=AssertionError("should not call")
        ),
    ):
        result = valid_skill.format_briefing()
    assert mock_digest_text in result
    assert "No ideas available." in result


# ---------------------------------------------------------------------------
# generate_briefing — both empty feed_urls and empty idea_topic
# ---------------------------------------------------------------------------


def test_generate_briefing_with_empty_feed_urls_and_empty_idea_topic() -> None:
    skill = BriefingSkill(feed_urls=[], idea_topic="")
    with (
        patch.object(DigestSkill, "generate_digest", return_value=""),
        patch.object(IdeaGeneratorSkill, "format_report", return_value=""),
    ):
        result = skill.generate_briefing()
    assert "=== PM Daily Briefing ===" in result
    assert "--- Ideas ---" in result
