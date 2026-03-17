"""Telegram bot application setup."""

from __future__ import annotations

import logging

from telegram.ext import Application, CommandHandler

from src.bot.handlers import cmd_help, cmd_start
from src.config.settings import get_telegram_token

logger = logging.getLogger(__name__)


def create_app() -> Application:
    """Creates and configures the Telegram bot application."""
    token = get_telegram_token()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))

    logger.info("Bot application created with %d handlers", len(app.handlers[0]))
    return app
