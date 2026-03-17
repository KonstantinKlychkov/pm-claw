"""Telegram bot application factory."""

from __future__ import annotations

import os

from telegram.ext import Application, CommandHandler

from src.bot.handlers import start


def create_app() -> Application:
    """Create and configure the Telegram bot application.

    Reads the bot token from the TELEGRAM_BOT_TOKEN environment variable
    and registers command handlers.

    Returns:
        Configured Application instance ready for polling.

    Raises:
        ValueError: If TELEGRAM_BOT_TOKEN is not set, empty, or whitespace-only.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token.strip():
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is not set. "
            "Create a .env file with your bot token."
        )

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    return app
