"""Tests for src/skills/__init__.py — SKILL_REGISTRY."""

from __future__ import annotations

import pytest

from src.skills import SKILL_REGISTRY


# ---------------------------------------------------------------------------
# Registry structure — keys
# ---------------------------------------------------------------------------


def test_skill_registry_has_exactly_four_entries() -> None:
    """SKILL_REGISTRY contains exactly 4 skill entries."""
    assert len(SKILL_REGISTRY) == 4


def test_skill_registry_contains_digest_key() -> None:
    """SKILL_REGISTRY has a 'digest' entry."""
    assert "digest" in SKILL_REGISTRY


def test_skill_registry_contains_ideas_key() -> None:
    """SKILL_REGISTRY has an 'ideas' entry."""
    assert "ideas" in SKILL_REGISTRY


def test_skill_registry_contains_competitor_key() -> None:
    """SKILL_REGISTRY has a 'competitor' entry."""
    assert "competitor" in SKILL_REGISTRY


def test_skill_registry_contains_briefing_key() -> None:
    """SKILL_REGISTRY has a 'briefing' entry."""
    assert "briefing" in SKILL_REGISTRY


# ---------------------------------------------------------------------------
# Registry structure — required fields per entry
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ["digest", "ideas", "competitor", "briefing"])
def test_skill_registry_entry_has_description_field(key: str) -> None:
    """Each SKILL_REGISTRY entry exposes a non-empty 'description'."""
    assert SKILL_REGISTRY[key]["description"]


@pytest.mark.parametrize("key", ["digest", "ideas", "competitor", "briefing"])
def test_skill_registry_entry_has_usage_field(key: str) -> None:
    """Each SKILL_REGISTRY entry exposes a non-empty 'usage'."""
    assert SKILL_REGISTRY[key]["usage"]


# ---------------------------------------------------------------------------
# Registry — description and usage are strings
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ["digest", "ideas", "competitor", "briefing"])
def test_skill_registry_description_is_a_string(key: str) -> None:
    """'description' value in each entry is a str."""
    assert isinstance(SKILL_REGISTRY[key]["description"], str)


@pytest.mark.parametrize("key", ["digest", "ideas", "competitor", "briefing"])
def test_skill_registry_usage_is_a_string(key: str) -> None:
    """'usage' value in each entry is a str."""
    assert isinstance(SKILL_REGISTRY[key]["usage"], str)


# ---------------------------------------------------------------------------
# Registry — usage strings contain the matching slash command
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ["digest", "ideas", "competitor", "briefing"])
def test_skill_registry_usage_contains_slash_command(key: str) -> None:
    """'usage' string starts with the slash command for that skill."""
    assert SKILL_REGISTRY[key]["usage"].startswith(f"/{key}")
