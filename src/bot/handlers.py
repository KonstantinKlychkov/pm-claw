"""Telegram bot command handlers."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command.

    Args:
        update: Incoming Telegram update.
        context: Callback context from python-telegram-bot.
    """
    if update.message is None:
        return
    text = "PM Claw Bot\n\nNo skills available yet."
    await update.message.reply_text(text)
