"""Tests for src/bot/app.py — bot application factory."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from telegram.ext import Application, CommandHandler

from src.bot.handlers import cmd_help, cmd_start


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """Returns a configured Application instance with a fake token."""
    with patch("src.bot.app.get_telegram_token", return_value="fake:token123"):
        from src.bot.app import create_app

        return create_app()


# ---------------------------------------------------------------------------
# create_app — return type
# ---------------------------------------------------------------------------


def test_create_app_returns_application_instance(app: Application) -> None:
    """create_app returns a telegram.ext.Application object."""
    assert isinstance(app, Application)


# ---------------------------------------------------------------------------
# create_app — number of registered handlers
# ---------------------------------------------------------------------------


def test_create_app_registers_two_handlers(app: Application) -> None:
    """create_app registers exactly 2 CommandHandlers in group 0."""
    assert len(app.handlers[0]) == 2


# ---------------------------------------------------------------------------
# create_app — each expected command is registered
# ---------------------------------------------------------------------------


def _registered_commands(app: Application) -> set[str]:
    """Helper: collect all command names registered in handler group 0."""
    commands: set[str] = set()
    for handler in app.handlers[0]:
        if isinstance(handler, CommandHandler):
            commands.update(handler.commands)
    return commands


def test_create_app_registers_start_command(app: Application) -> None:
    """create_app registers the /start command."""
    assert "start" in _registered_commands(app)


def test_create_app_registers_help_command(app: Application) -> None:
    """create_app registers the /help command."""
    assert "help" in _registered_commands(app)


# ---------------------------------------------------------------------------
# create_app — handlers are bound to the correct callback functions
# ---------------------------------------------------------------------------


def _callback_for_command(app: Application, command: str):
    """Helper: return the callback for a given slash command, or None."""
    for handler in app.handlers[0]:
        if isinstance(handler, CommandHandler) and command in handler.commands:
            return handler.callback
    return None


def test_create_app_start_command_uses_cmd_start(app: Application) -> None:
    """create_app binds /start to cmd_start handler."""
    assert _callback_for_command(app, "start") is cmd_start


def test_create_app_help_command_uses_cmd_help(app: Application) -> None:
    """create_app binds /help to cmd_help handler."""
    assert _callback_for_command(app, "help") is cmd_help


# ---------------------------------------------------------------------------
# create_app — token propagation
# -------------------------------------------------https://github.com/KonstantinKlychkov/pm-claw/pull/11/conflict?name=tests%252Ftest_bot_app.py&base_oid=049b8e2311294c713c31edc1f48a3213fd1cfa32&head_oid=b8f68378c2d2e51a5d18c79865a903d0ad6fd4a1--------------------------


def test_create_app_calls_get_telegram_token() -> None:
    """create_app invokes get_telegram_token exactly once to retrieve the token."""
    with patch("src.bot.app.get_telegram_token", return_value="fake:token456") as mock_token:
        from src.bot.app import create_app

        create_app()

    mock_token.assert_called_once()


# ---------------------------------------------------------------------------
# create_app — all handlers are CommandHandler instances
# ---------------------------------------------------------------------------


def test_create_app_all_handlers_are_command_handlers(app: Application) -> None:
    """Every handler registered by create_app is a CommandHandler."""
    for handler in app.handlers[0]:
        assert isinstance(handler, CommandHandler)
