"""Application settings loaded from environment variables."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def get_telegram_token() -> str:
    """Returns the Telegram bot token or raises ValueError if not set."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set. Add it to .env file.")
    return token


DEFAULT_FEED_URLS: list[str] = [
    url.strip()
    for url in os.environ.get("FEED_URLS", "").split(",")
    if url.strip()
]
