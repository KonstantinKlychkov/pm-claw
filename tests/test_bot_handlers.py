"""Tests for Telegram bot command handlers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.bot.handlers import start


@pytest.fixture
def update() -> MagicMock:
    """Create a mock Telegram Update with async reply_text."""
    mock_update = MagicMock()
    mock_update.message = MagicMock()
    mock_update.message.reply_text = AsyncMock()
    return mock_update


@pytest.fixture
def context() -> MagicMock:
    """Create a mock callback context."""
    return MagicMock()


@pytest.mark.asyncio
async def test_start_sends_greeting(
    update: MagicMock, context: MagicMock
) -> None:
    """Start handler should call reply_text exactly once."""
    await start(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_start_message_contains_no_skills(
    update: MagicMock, context: MagicMock
) -> None:
    """Start handler should mention that no skills are available."""
    await start(update, context)
    text = update.message.reply_text.call_args[0][0]
    assert "No skills available yet" in text


@pytest.mark.asyncio
async def test_start_message_contains_bot_name(
    update: MagicMock, context: MagicMock
) -> None:
    """Start handler should include the bot name."""
    await start(update, context)
    text = update.message.reply_text.call_args[0][0]
    assert "PM Claw" in text


@pytest.mark.asyncio
async def test_start_with_no_message_does_not_raise(
    context: MagicMock,
) -> None:
    """Start handler should return silently when update.message is None."""
    mock_update = MagicMock()
    mock_update.message = None
    await start(mock_update, context)
