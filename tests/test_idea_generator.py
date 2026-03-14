"""Tests for IdeaGeneratorSkill and module-level helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from src.skills.idea_generator import (
    SCAMPER_PROMPTS,
    IdeaGeneratorSkill,
    _format_markdown,
    _format_report,
    _slugify,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_skill() -> IdeaGeneratorSkill:
    """IdeaGeneratorSkill pre-loaded with a normal topic."""
    return IdeaGeneratorSkill(topic="online grocery delivery")


@pytest.fixture
def generated_skill(valid_skill: IdeaGeneratorSkill) -> IdeaGeneratorSkill:
    """IdeaGeneratorSkill that has already generated ideas."""
    valid_skill.generate_scamper_ideas()
    return valid_skill


@pytest.fixture
def sample_ideas() -> dict[str, str]:
    """Minimal ideas dict for helper-function tests."""
    return {category: f"Prompt for {category}" for category in SCAMPER_PROMPTS}


# ---------------------------------------------------------------------------
# generate_scamper_ideas — happy path
# ---------------------------------------------------------------------------


def test_generate_scamper_ideas_with_valid_topic_returns_all_categories(
    valid_skill: IdeaGeneratorSkill,
) -> None:
    ideas = valid_skill.generate_scamper_ideas()
    assert set(ideas.keys()) == set(SCAMPER_PROMPTS.keys())


def test_generate_scamper_ideas_with_valid_topic_returns_seven_items(
    valid_skill: IdeaGeneratorSkill,
) -> None:
    ideas = valid_skill.generate_scamper_ideas()
    assert len(ideas) == 7


def test_generate_scamper_ideas_embeds_topic_in_each_prompt(
    valid_skill: IdeaGeneratorSkill,
) -> None:
    ideas = valid_skill.generate_scamper_ideas()
    for category, prompt in ideas.items():
        assert "online grocery delivery" in prompt, (
            f"Topic not embedded in category '{category}'"
        )


def test_generate_scamper_ideas_does_not_append_error_for_valid_topic(
    valid_skill: IdeaGeneratorSkill,
) -> None:
    valid_skill.generate_scamper_ideas()
    assert valid_skill._errors == []


def test_generate_scamper_ideas_strips_surrounding_whitespace_from_topic() -> None:
    skill = IdeaGeneratorSkill(topic="  drone delivery  ")
    ideas = skill.generate_scamper_ideas()
    for prompt in ideas.values():
        assert "drone delivery" in prompt
        assert "  drone delivery  " not in prompt


# ---------------------------------------------------------------------------
# generate_scamper_ideas — empty / whitespace topic
# ---------------------------------------------------------------------------


def test_generate_scamper_ideas_with_empty_topic_returns_empty_dict() -> None:
    skill = IdeaGeneratorSkill(topic="")
    ideas = skill.generate_scamper_ideas()
    assert ideas == {}


def test_generate_scamper_ideas_with_whitespace_topic_returns_empty_dict() -> None:
    skill = IdeaGeneratorSkill(topic="   ")
    ideas = skill.generate_scamper_ideas()
    assert ideas == {}


def test_generate_scamper_ideas_with_empty_topic_appends_error() -> None:
    skill = IdeaGeneratorSkill(topic="")
    skill.generate_scamper_ideas()
    assert len(skill._errors) == 1
    assert "empty" in skill._errors[0].lower()


def test_generate_scamper_ideas_with_whitespace_topic_appends_error() -> None:
    skill = IdeaGeneratorSkill(topic="   ")
    skill.generate_scamper_ideas()
    assert len(skill._errors) == 1


# ---------------------------------------------------------------------------
# save_to_markdown — happy path (uses tmp_path)
# ---------------------------------------------------------------------------


def test_save_to_markdown_creates_file_in_output_dir(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    result = generated_skill.save_to_markdown(output_dir=str(tmp_path))
    assert result != ""
    assert Path(result).exists()


def test_save_to_markdown_creates_directory_if_missing(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    nested = str(tmp_path / "level1" / "level2")
    result = generated_skill.save_to_markdown(output_dir=nested)
    assert Path(result).exists()


def test_save_to_markdown_file_contains_topic(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    result = generated_skill.save_to_markdown(output_dir=str(tmp_path))
    content = Path(result).read_text(encoding="utf-8")
    assert "online grocery delivery" in content


def test_save_to_markdown_file_contains_all_categories(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    result = generated_skill.save_to_markdown(output_dir=str(tmp_path))
    content = Path(result).read_text(encoding="utf-8")
    for category in SCAMPER_PROMPTS:
        assert category in content, f"Category '{category}' missing from markdown file"


def test_save_to_markdown_returns_string_path(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    result = generated_skill.save_to_markdown(output_dir=str(tmp_path))
    assert isinstance(result, str)
    assert result.endswith(".md")


# ---------------------------------------------------------------------------
# save_to_markdown — auto-generates ideas if not yet produced
# ---------------------------------------------------------------------------


def test_save_to_markdown_auto_generates_ideas_when_not_yet_generated(
    valid_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    assert valid_skill._ideas == {}
    result = valid_skill.save_to_markdown(output_dir=str(tmp_path))
    assert result != ""
    assert Path(result).exists()


def test_save_to_markdown_with_empty_topic_returns_empty_string(
    tmp_path: Path,
) -> None:
    skill = IdeaGeneratorSkill(topic="")
    result = skill.save_to_markdown(output_dir=str(tmp_path))
    assert result == ""


# ---------------------------------------------------------------------------
# save_to_markdown — IO error handling
# ---------------------------------------------------------------------------


def test_save_to_markdown_returns_empty_string_on_write_error(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    with patch("src.skills.idea_generator.Path.write_text", side_effect=OSError("disk full")):
        result = generated_skill.save_to_markdown(output_dir=str(tmp_path))
    assert result == ""


def test_save_to_markdown_appends_error_on_write_failure(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    with patch("src.skills.idea_generator.Path.write_text", side_effect=OSError("disk full")):
        generated_skill.save_to_markdown(output_dir=str(tmp_path))
    assert any("write" in e.lower() or "disk full" in e.lower() for e in generated_skill._errors)


def test_save_to_markdown_returns_empty_string_on_mkdir_error(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    with patch("src.skills.idea_generator.Path.mkdir", side_effect=OSError("permission denied")):
        result = generated_skill.save_to_markdown(output_dir=str(tmp_path / "blocked"))
    assert result == ""


def test_save_to_markdown_appends_error_on_mkdir_failure(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    with patch("src.skills.idea_generator.Path.mkdir", side_effect=OSError("permission denied")):
        generated_skill.save_to_markdown(output_dir=str(tmp_path / "blocked"))
    assert any("directory" in e.lower() for e in generated_skill._errors)


# ---------------------------------------------------------------------------
# format_report — happy path
# ---------------------------------------------------------------------------


def test_format_report_with_valid_topic_contains_topic(
    valid_skill: IdeaGeneratorSkill,
) -> None:
    report = valid_skill.format_report()
    assert "online grocery delivery" in report


def test_format_report_with_valid_topic_contains_all_categories(
    valid_skill: IdeaGeneratorSkill,
) -> None:
    report = valid_skill.format_report()
    for category in SCAMPER_PROMPTS:
        assert category in report, f"Category '{category}' missing from report"


def test_format_report_returns_string(valid_skill: IdeaGeneratorSkill) -> None:
    result = valid_skill.format_report()
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# format_report — auto-generates ideas if not yet produced
# ---------------------------------------------------------------------------


def test_format_report_auto_generates_ideas_when_not_yet_generated(
    valid_skill: IdeaGeneratorSkill,
) -> None:
    assert valid_skill._ideas == {}
    report = valid_skill.format_report()
    assert "online grocery delivery" in report


# ---------------------------------------------------------------------------
# format_report — empty / invalid topic
# ---------------------------------------------------------------------------


def test_format_report_with_empty_topic_returns_no_ideas_message() -> None:
    skill = IdeaGeneratorSkill(topic="")
    result = skill.format_report()
    assert "No ideas generated" in result


def test_format_report_with_whitespace_topic_returns_no_ideas_message() -> None:
    skill = IdeaGeneratorSkill(topic="   ")
    result = skill.format_report()
    assert "No ideas generated" in result


def test_format_report_with_empty_topic_includes_error_detail() -> None:
    skill = IdeaGeneratorSkill(topic="")
    result = skill.format_report()
    assert "Topic cannot be empty" in result


# ---------------------------------------------------------------------------
# _slugify
# ---------------------------------------------------------------------------


def test_slugify_converts_spaces_to_hyphens() -> None:
    assert _slugify("hello world") == "hello-world"


def test_slugify_converts_to_lowercase() -> None:
    assert _slugify("HelloWorld") == "helloworld"


def test_slugify_strips_special_characters() -> None:
    result = _slugify("idea! @#$%^&*()")
    assert "!" not in result
    assert "@" not in result
    assert "#" not in result


def test_slugify_handles_underscores_as_hyphens() -> None:
    result = _slugify("hello_world")
    assert result == "hello-world"


def test_slugify_strips_leading_and_trailing_hyphens() -> None:
    result = _slugify("  --hello world--  ")
    assert not result.startswith("-")
    assert not result.endswith("-")


def test_slugify_respects_max_length_default() -> None:
    long_text = "word " * 20
    result = _slugify(long_text)
    assert len(result) <= 50


def test_slugify_respects_custom_max_length() -> None:
    result = _slugify("hello world foo bar baz", max_length=10)
    assert len(result) <= 10


def test_slugify_with_empty_string_returns_empty() -> None:
    assert _slugify("") == ""


def test_slugify_with_only_special_chars_returns_empty_or_hyphen_stripped() -> None:
    result = _slugify("!@#$%^&*()")
    assert result == ""


def test_slugify_with_mixed_whitespace_collapses_to_single_hyphen() -> None:
    result = _slugify("hello   world")
    assert "--" not in result
    assert "hello-world" == result


# ---------------------------------------------------------------------------
# _format_markdown
# ---------------------------------------------------------------------------


def test_format_markdown_contains_topic_in_heading(sample_ideas: dict[str, str]) -> None:
    result = _format_markdown("my product", sample_ideas)
    assert "# Idea Generation: my product" in result


def test_format_markdown_contains_date_line(sample_ideas: dict[str, str]) -> None:
    result = _format_markdown("my product", sample_ideas)
    assert "**Date:**" in result


def test_format_markdown_contains_framework_name(sample_ideas: dict[str, str]) -> None:
    result = _format_markdown("my product", sample_ideas)
    assert "SCAMPER" in result


def test_format_markdown_contains_all_category_headings(sample_ideas: dict[str, str]) -> None:
    result = _format_markdown("my product", sample_ideas)
    for category in sample_ideas:
        assert f"## {category}" in result, f"Heading for '{category}' missing"


def test_format_markdown_contains_all_prompts(sample_ideas: dict[str, str]) -> None:
    result = _format_markdown("my product", sample_ideas)
    for prompt in sample_ideas.values():
        assert prompt in result


def test_format_markdown_uses_current_utc_date(sample_ideas: dict[str, str]) -> None:
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    result = _format_markdown("my product", sample_ideas)
    assert today in result


# ---------------------------------------------------------------------------
# _format_report
# ---------------------------------------------------------------------------


def test_format_report_helper_contains_scamper_header(sample_ideas: dict[str, str]) -> None:
    result = _format_report("my product", sample_ideas)
    assert "SCAMPER Ideas: my product" in result


def test_format_report_helper_contains_all_categories(sample_ideas: dict[str, str]) -> None:
    result = _format_report("my product", sample_ideas)
    for category in sample_ideas:
        assert f"[{category}]" in result, f"Category label '[{category}]' missing"


def test_format_report_helper_contains_all_prompts(sample_ideas: dict[str, str]) -> None:
    result = _format_report("my product", sample_ideas)
    for prompt in sample_ideas.values():
        assert prompt in result


def test_format_report_helper_returns_plain_text_no_markdown_headers(
    sample_ideas: dict[str, str],
) -> None:
    result = _format_report("my product", sample_ideas)
    assert "## " not in result
    assert "**" not in result


def test_format_report_helper_does_not_end_with_newline(
    sample_ideas: dict[str, str],
) -> None:
    result = _format_report("my product", sample_ideas)
    assert not result.endswith("\n")


# ---------------------------------------------------------------------------
# Regression: stale _ideas on repeated calls
# ---------------------------------------------------------------------------


def test_generate_scamper_ideas_accumulates_errors_across_calls() -> None:
    skill = IdeaGeneratorSkill(topic="")
    skill.generate_scamper_ideas()
    skill.generate_scamper_ideas()
    assert len(skill._errors) == 2


def test_generate_scamper_ideas_clears_stale_ideas_on_empty_topic() -> None:
    skill = IdeaGeneratorSkill(topic="valid topic")
    skill.generate_scamper_ideas()
    assert len(skill._ideas) == 7

    skill.topic = ""
    skill.generate_scamper_ideas()
    assert skill._ideas == {}


# ---------------------------------------------------------------------------
# Regression: _slugify trailing hyphen after truncation
# ---------------------------------------------------------------------------


def test_slugify_no_trailing_hyphen_after_truncation() -> None:
    result = _slugify("hello-world-foo", max_length=12)
    assert not result.endswith("-")


# ---------------------------------------------------------------------------
# save_to_markdown — path traversal guard
# ---------------------------------------------------------------------------


def test_save_to_markdown_rejects_path_outside_base_dir(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    base = tmp_path / "allowed"
    base.mkdir()
    outside = tmp_path / "forbidden"
    outside.mkdir()
    result = generated_skill.save_to_markdown(
        output_dir=str(outside), base_dir=str(base)
    )
    assert result == ""
    assert any("outside" in e.lower() for e in generated_skill._errors)


def test_save_to_markdown_rejects_path_with_prefix_collision(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    base = tmp_path / "allowed"
    base.mkdir()
    poison = tmp_path / "allowed_poison"
    poison.mkdir()
    result = generated_skill.save_to_markdown(
        output_dir=str(poison), base_dir=str(base)
    )
    assert result == ""


def test_save_to_markdown_allows_path_inside_base_dir(
    generated_skill: IdeaGeneratorSkill, tmp_path: Path
) -> None:
    base = tmp_path / "project"
    output = base / "docs" / "ideas"
    base.mkdir()
    result = generated_skill.save_to_markdown(
        output_dir=str(output), base_dir=str(base)
    )
    assert result != ""
    assert Path(result).exists()
