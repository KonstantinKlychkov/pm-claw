"""Tests for src/config/settings.py."""

from __future__ import annotations

import sys
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# get_telegram_token — happy path
# ---------------------------------------------------------------------------


def test_get_telegram_token_with_env_set_returns_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_telegram_token returns the token string when the env var is present."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-bot-token-123")

    # Re-import inside the test so os.environ.get picks up the patched value.
    from src.config.settings import get_telegram_token

    assert get_telegram_token() == "test-bot-token-123"


def test_get_telegram_token_returns_exact_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_telegram_token returns the token without modification."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "  spaces-preserved  ")

    from src.config.settings import get_telegram_token

    assert get_telegram_token() == "  spaces-preserved  "


# ---------------------------------------------------------------------------
# get_telegram_token — missing token exits
# ---------------------------------------------------------------------------


def test_get_telegram_token_without_env_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_telegram_token raises ValueError when the env var is absent."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    from src.config.settings import get_telegram_token

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is not set"):
        get_telegram_token()


def test_get_telegram_token_with_empty_string_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """get_telegram_token raises ValueError when token is an empty string."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")

    from src.config.settings import get_telegram_token

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is not set"):
        get_telegram_token()


# ---------------------------------------------------------------------------
# DEFAULT_FEED_URLS — env var parsing
# ---------------------------------------------------------------------------


def test_default_feed_urls_with_single_url_returns_one_element(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DEFAULT_FEED_URLS contains exactly one entry when FEED_URLS has one URL."""
    monkeypatch.setenv("FEED_URLS", "https://example.com/rss")

    # Force re-evaluation by reloading the module.
    import importlib

    import src.config.settings as settings_mod

    importlib.reload(settings_mod)

    assert settings_mod.DEFAULT_FEED_URLS == ["https://example.com/rss"]


def test_default_feed_urls_with_multiple_urls_splits_on_comma(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DEFAULT_FEED_URLS splits a comma-separated FEED_URLS into multiple entries."""
    monkeypatch.setenv("FEED_URLS", "https://a.com/rss,https://b.com/feed")

    import importlib

    import src.config.settings as settings_mod

    importlib.reload(settings_mod)

    assert settings_mod.DEFAULT_FEED_URLS == ["https://a.com/rss", "https://b.com/feed"]


def test_default_feed_urls_strips_whitespace_around_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DEFAULT_FEED_URLS strips surrounding whitespace from each URL."""
    monkeypatch.setenv("FEED_URLS", "  https://a.com/rss ,  https://b.com/feed  ")

    import importlib

    import src.config.settings as settings_mod

    importlib.reload(settings_mod)

    assert settings_mod.DEFAULT_FEED_URLS == ["https://a.com/rss", "https://b.com/feed"]


def test_default_feed_urls_with_empty_env_returns_empty_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DEFAULT_FEED_URLS is empty when FEED_URLS is not set."""
    monkeypatch.delenv("FEED_URLS", raising=False)

    import importlib

    import src.config.settings as settings_mod

    importlib.reload(settings_mod)

    assert settings_mod.DEFAULT_FEED_URLS == []


def test_default_feed_urls_skips_blank_entries_between_commas(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DEFAULT_FEED_URLS ignores blank entries produced by consecutive commas."""
    monkeypatch.setenv("FEED_URLS", "https://a.com/rss,,https://b.com/feed,")

    import importlib

    import src.config.settings as settings_mod

    importlib.reload(settings_mod)

    assert settings_mod.DEFAULT_FEED_URLS == ["https://a.com/rss", "https://b.com/feed"]


def test_default_feed_urls_is_a_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """DEFAULT_FEED_URLS is always a list, never None or another type."""
    monkeypatch.delenv("FEED_URLS", raising=False)

    import importlib

    import src.config.settings as settings_mod

    importlib.reload(settings_mod)

    assert isinstance(settings_mod.DEFAULT_FEED_URLS, list)
