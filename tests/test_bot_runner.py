"""Tests for the bot runner entry point."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.bot_runner import main


def test_main_calls_create_app_and_run_polling(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """main() should create the app and start polling."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token-123")
    mock_app = MagicMock()
    with (
        patch("src.bot_runner.load_dotenv"),
        patch("src.bot_runner.create_app", return_value=mock_app) as mock_create,
    ):
        main()
    mock_create.assert_called_once()
    mock_app.run_polling.assert_called_once()


def test_main_exits_on_missing_token() -> None:
    """main() should exit with code 1 when token is missing."""
    with (
        patch("src.bot_runner.load_dotenv"),
        patch("src.bot_runner.create_app", side_effect=ValueError("no token")),
        pytest.raises(SystemExit, match="1"),
    ):
        main()
