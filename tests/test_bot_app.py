"""Tests for Telegram bot application factory."""

from __future__ import annotations

import pytest

from src.bot.bot import create_app


@pytest.fixture(autouse=True)
def _clear_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure TELEGRAM_BOT_TOKEN is unset before each test."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)


def test_create_app_without_token_raises_value_error() -> None:
    """create_app should raise ValueError when token is missing."""
    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
        create_app()


def test_create_app_with_empty_token_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """create_app should raise ValueError when token is empty string."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
        create_app()


def test_create_app_with_whitespace_token_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """create_app should raise ValueError when token is whitespace-only."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "   ")
    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
        create_app()


def test_create_app_with_valid_token_returns_application(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """create_app should return an Application with a valid token."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token-123")
    app = create_app()
    assert app is not None


def test_create_app_registers_start_handler(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """create_app should register a /start command handler."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token-123")
    app = create_app()
    handlers = app.handlers.get(0, [])
    commands = [h.commands for h in handlers if hasattr(h, "commands")]
    assert any("start" in cmd_set for cmd_set in commands)
