"""Tests for CompetitorSkill and module-level helpers."""

from __future__ import annotations

import pytest

from src.skills.competitor_skill import (
    CompetitorSkill,
    _format_analysis_report,
    _format_comparison,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_skill() -> CompetitorSkill:
    """CompetitorSkill with a normal product name."""
    return CompetitorSkill(product_name="Notion")


@pytest.fixture
def analyzed_skill(valid_skill: CompetitorSkill) -> CompetitorSkill:
    """CompetitorSkill that has already run analyze()."""
    valid_skill.analyze()
    return valid_skill


@pytest.fixture
def sample_analysis() -> dict:
    """Minimal analysis dict for helper-function tests."""
    return {
        "product_name": "Notion",
        "description": "Overview of Notion — add details from research.",
        "key_features": [
            "Feature 1 of Notion",
            "Feature 2 of Notion",
            "Feature 3 of Notion",
        ],
        "strengths": [
            "Strength 1 of Notion",
            "Strength 2 of Notion",
        ],
        "weaknesses": [
            "Weakness 1 of Notion",
            "Weakness 2 of Notion",
        ],
        "pricing_model": "Pricing model for Notion — add details from research.",
    }


# ---------------------------------------------------------------------------
# analyze — happy path
# ---------------------------------------------------------------------------


def test_analyze_with_valid_product_returns_all_expected_keys(
    valid_skill: CompetitorSkill,
) -> None:
    result = valid_skill.analyze()
    expected_keys = {"product_name", "description", "key_features", "strengths", "weaknesses",
                     "pricing_model"}
    assert set(result.keys()) == expected_keys


def test_analyze_with_valid_product_returns_correct_product_name(
    valid_skill: CompetitorSkill,
) -> None:
    result = valid_skill.analyze()
    assert result["product_name"] == "Notion"


def test_analyze_with_valid_product_returns_three_key_features(
    valid_skill: CompetitorSkill,
) -> None:
    result = valid_skill.analyze()
    assert len(result["key_features"]) == 3


def test_analyze_with_valid_product_returns_two_strengths(
    valid_skill: CompetitorSkill,
) -> None:
    result = valid_skill.analyze()
    assert len(result["strengths"]) == 2


def test_analyze_with_valid_product_returns_two_weaknesses(
    valid_skill: CompetitorSkill,
) -> None:
    result = valid_skill.analyze()
    assert len(result["weaknesses"]) == 2


def test_analyze_with_valid_product_does_not_append_error(
    valid_skill: CompetitorSkill,
) -> None:
    valid_skill.analyze()
    assert valid_skill._errors == []


# ---------------------------------------------------------------------------
# analyze — caching
# ---------------------------------------------------------------------------


def test_analyze_caches_result_in_analysis_field(valid_skill: CompetitorSkill) -> None:
    valid_skill.analyze()
    assert valid_skill._analysis is not None


def test_analyze_cached_result_equals_returned_dict(valid_skill: CompetitorSkill) -> None:
    result = valid_skill.analyze()
    assert valid_skill._analysis == result


# ---------------------------------------------------------------------------
# analyze — invalid input
# ---------------------------------------------------------------------------


def test_analyze_with_empty_product_name_returns_empty_dict() -> None:
    skill = CompetitorSkill(product_name="")
    result = skill.analyze()
    assert result == {}


def test_analyze_with_whitespace_product_name_returns_empty_dict() -> None:
    skill = CompetitorSkill(product_name="   ")
    result = skill.analyze()
    assert result == {}


def test_analyze_with_empty_product_name_appends_error() -> None:
    skill = CompetitorSkill(product_name="")
    skill.analyze()
    assert len(skill._errors) == 1


def test_analyze_with_whitespace_product_name_appends_error() -> None:
    skill = CompetitorSkill(product_name="   ")
    skill.analyze()
    assert len(skill._errors) == 1


# ---------------------------------------------------------------------------
# analyze — whitespace stripping
# ---------------------------------------------------------------------------


def test_analyze_strips_whitespace_from_product_name() -> None:
    skill = CompetitorSkill(product_name="  Notion  ")
    result = skill.analyze()
    assert result["product_name"] == "Notion"


def test_analyze_strips_whitespace_and_embeds_clean_name_in_features() -> None:
    skill = CompetitorSkill(product_name="  Notion  ")
    result = skill.analyze()
    for feature in result["key_features"]:
        assert "Notion" in feature
        assert "  Notion  " not in feature


# ---------------------------------------------------------------------------
# analyze — repeated calls with empty name accumulate errors
# ---------------------------------------------------------------------------


def test_analyze_repeated_calls_with_empty_name_accumulate_errors() -> None:
    skill = CompetitorSkill(product_name="")
    skill.analyze()
    skill.analyze()
    assert len(skill._errors) == 2


# ---------------------------------------------------------------------------
# format_report — happy path
# ---------------------------------------------------------------------------


def test_format_report_contains_product_name(analyzed_skill: CompetitorSkill) -> None:
    report = analyzed_skill.format_report()
    assert "Notion" in report


def test_format_report_contains_description_section(analyzed_skill: CompetitorSkill) -> None:
    report = analyzed_skill.format_report()
    assert "[Description]" in report


def test_format_report_contains_key_features_section(analyzed_skill: CompetitorSkill) -> None:
    report = analyzed_skill.format_report()
    assert "[Key Features]" in report


def test_format_report_contains_strengths_section(analyzed_skill: CompetitorSkill) -> None:
    report = analyzed_skill.format_report()
    assert "[Strengths]" in report


def test_format_report_contains_weaknesses_section(analyzed_skill: CompetitorSkill) -> None:
    report = analyzed_skill.format_report()
    assert "[Weaknesses]" in report


def test_format_report_contains_pricing_model_section(analyzed_skill: CompetitorSkill) -> None:
    report = analyzed_skill.format_report()
    assert "[Pricing Model]" in report


def test_format_report_returns_string(analyzed_skill: CompetitorSkill) -> None:
    result = analyzed_skill.format_report()
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# format_report — auto-generates analysis when not yet cached
# ---------------------------------------------------------------------------


def test_format_report_auto_generates_analysis_when_not_cached(
    valid_skill: CompetitorSkill,
) -> None:
    assert valid_skill._analysis is None
    report = valid_skill.format_report()
    assert "Notion" in report


def test_format_report_sets_analysis_cache_after_auto_generate(
    valid_skill: CompetitorSkill,
) -> None:
    assert valid_skill._analysis is None
    valid_skill.format_report()
    assert valid_skill._analysis is not None


# ---------------------------------------------------------------------------
# format_report — empty product name
# ---------------------------------------------------------------------------


def test_format_report_with_empty_name_returns_no_analysis_available() -> None:
    skill = CompetitorSkill(product_name="")
    result = skill.format_report()
    assert "No analysis available" in result


def test_format_report_with_whitespace_name_returns_no_analysis_available() -> None:
    skill = CompetitorSkill(product_name="   ")
    result = skill.format_report()
    assert "No analysis available" in result


# ---------------------------------------------------------------------------
# compare — happy path
# ---------------------------------------------------------------------------


def test_compare_with_two_analyzed_skills_contains_first_product_name() -> None:
    skill_a = CompetitorSkill(product_name="Notion")
    skill_b = CompetitorSkill(product_name="Confluence")
    skill_a.analyze()
    skill_b.analyze()
    result = skill_a.compare(skill_b)
    assert "Notion" in result


def test_compare_with_two_analyzed_skills_contains_second_product_name() -> None:
    skill_a = CompetitorSkill(product_name="Notion")
    skill_b = CompetitorSkill(product_name="Confluence")
    skill_a.analyze()
    skill_b.analyze()
    result = skill_a.compare(skill_b)
    assert "Confluence" in result


def test_compare_with_two_analyzed_skills_contains_both_product_names() -> None:
    skill_a = CompetitorSkill(product_name="Notion")
    skill_b = CompetitorSkill(product_name="Confluence")
    skill_a.analyze()
    skill_b.analyze()
    result = skill_a.compare(skill_b)
    assert "Notion" in result and "Confluence" in result


# ---------------------------------------------------------------------------
# compare — missing analysis
# ---------------------------------------------------------------------------


def test_compare_returns_error_when_self_has_empty_product_name() -> None:
    skill_a = CompetitorSkill(product_name="")
    skill_b = CompetitorSkill(product_name="Confluence")
    skill_b.analyze()
    result = skill_a.compare(skill_b)
    assert "Error" in result


def test_compare_returns_error_when_other_has_empty_product_name() -> None:
    skill_a = CompetitorSkill(product_name="Notion")
    skill_b = CompetitorSkill(product_name="")
    skill_a.analyze()
    result = skill_a.compare(skill_b)
    assert "Error" in result


def test_compare_auto_analyzes_self_when_not_cached() -> None:
    skill_a = CompetitorSkill(product_name="Notion")
    skill_b = CompetitorSkill(product_name="Confluence")
    skill_b.analyze()
    # skill_a is intentionally not analyzed before compare
    result = skill_a.compare(skill_b)
    assert "Notion" in result


def test_compare_auto_analyzes_other_when_not_cached() -> None:
    skill_a = CompetitorSkill(product_name="Notion")
    skill_b = CompetitorSkill(product_name="Confluence")
    skill_a.analyze()
    # skill_b is intentionally not analyzed before compare
    result = skill_a.compare(skill_b)
    assert "Confluence" in result


# ---------------------------------------------------------------------------
# _format_analysis_report — helper function
# ---------------------------------------------------------------------------


def test_format_analysis_report_contains_product_name(sample_analysis: dict) -> None:
    result = _format_analysis_report(sample_analysis)
    assert "Notion" in result


def test_format_analysis_report_contains_description_section(sample_analysis: dict) -> None:
    result = _format_analysis_report(sample_analysis)
    assert "[Description]" in result


def test_format_analysis_report_contains_key_features_section(sample_analysis: dict) -> None:
    result = _format_analysis_report(sample_analysis)
    assert "[Key Features]" in result


def test_format_analysis_report_contains_strengths_section(sample_analysis: dict) -> None:
    result = _format_analysis_report(sample_analysis)
    assert "[Strengths]" in result


def test_format_analysis_report_contains_weaknesses_section(sample_analysis: dict) -> None:
    result = _format_analysis_report(sample_analysis)
    assert "[Weaknesses]" in result


def test_format_analysis_report_contains_pricing_model_section(sample_analysis: dict) -> None:
    result = _format_analysis_report(sample_analysis)
    assert "[Pricing Model]" in result


def test_format_analysis_report_returns_plain_text_no_markdown_headers(
    sample_analysis: dict,
) -> None:
    result = _format_analysis_report(sample_analysis)
    assert "## " not in result
    assert "**" not in result


# ---------------------------------------------------------------------------
# _format_comparison — helper function
# ---------------------------------------------------------------------------


def test_format_comparison_contains_first_product(sample_analysis: dict) -> None:
    analysis_b = {
        "product_name": "Confluence",
        "description": "Overview of Confluence — add details from research.",
        "key_features": ["Feature 1 of Confluence", "Feature 2 of Confluence",
                         "Feature 3 of Confluence"],
        "strengths": ["Strength 1 of Confluence", "Strength 2 of Confluence"],
        "weaknesses": ["Weakness 1 of Confluence", "Weakness 2 of Confluence"],
        "pricing_model": "Pricing model for Confluence — add details from research.",
    }
    result = _format_comparison(sample_analysis, analysis_b)
    assert "Notion" in result


def test_format_comparison_contains_second_product(sample_analysis: dict) -> None:
    analysis_b = {
        "product_name": "Confluence",
        "description": "Overview of Confluence — add details from research.",
        "key_features": ["Feature 1 of Confluence", "Feature 2 of Confluence",
                         "Feature 3 of Confluence"],
        "strengths": ["Strength 1 of Confluence", "Strength 2 of Confluence"],
        "weaknesses": ["Weakness 1 of Confluence", "Weakness 2 of Confluence"],
        "pricing_model": "Pricing model for Confluence — add details from research.",
    }
    result = _format_comparison(sample_analysis, analysis_b)
    assert "Confluence" in result


def test_format_comparison_contains_both_products(sample_analysis: dict) -> None:
    analysis_b = {
        "product_name": "Confluence",
        "description": "Overview of Confluence — add details from research.",
        "key_features": ["Feature 1 of Confluence", "Feature 2 of Confluence",
                         "Feature 3 of Confluence"],
        "strengths": ["Strength 1 of Confluence", "Strength 2 of Confluence"],
        "weaknesses": ["Weakness 1 of Confluence", "Weakness 2 of Confluence"],
        "pricing_model": "Pricing model for Confluence — add details from research.",
    }
    result = _format_comparison(sample_analysis, analysis_b)
    assert "Notion" in result and "Confluence" in result


# ---------------------------------------------------------------------------
# analyze — mutation isolation
# ---------------------------------------------------------------------------


def test_analyze_returns_copy_not_reference(valid_skill: CompetitorSkill) -> None:
    result = valid_skill.analyze()
    result["product_name"] = "MUTATED"
    result["key_features"].append("INJECTED")
    assert valid_skill._analysis["product_name"] == "Notion"
    assert "INJECTED" not in valid_skill._analysis["key_features"]


# ---------------------------------------------------------------------------
# analyze — re-call refreshes analysis
# ---------------------------------------------------------------------------


def test_analyze_called_twice_returns_equal_dict_and_preserves_cache() -> None:
    skill = CompetitorSkill(product_name="Notion")
    first = skill.analyze()
    second = skill.analyze()
    assert first == second
    assert skill._analysis is not None


# ---------------------------------------------------------------------------
# format_report — error message includes detail
# ---------------------------------------------------------------------------


def test_format_report_with_empty_name_includes_error_detail() -> None:
    skill = CompetitorSkill(product_name="")
    result = skill.format_report()
    assert "Product name cannot be empty" in result


# ---------------------------------------------------------------------------
# compare — both skills have empty names
# ---------------------------------------------------------------------------


def test_compare_returns_error_when_both_have_empty_product_name() -> None:
    skill_a = CompetitorSkill(product_name="")
    skill_b = CompetitorSkill(product_name="")
    result = skill_a.compare(skill_b)
    assert "Error" in result


# ---------------------------------------------------------------------------
# _format_analysis_report — no trailing newline
# ---------------------------------------------------------------------------


def test_format_analysis_report_has_no_trailing_newline(sample_analysis: dict) -> None:
    result = _format_analysis_report(sample_analysis)
    assert not result.endswith("\n")


# ---------------------------------------------------------------------------
# _format_comparison — identical products
# ---------------------------------------------------------------------------


def test_format_comparison_with_identical_products(sample_analysis: dict) -> None:
    result = _format_comparison(sample_analysis, sample_analysis)
    assert "Notion" in result
    assert isinstance(result, str)
    assert len(result) > 0
