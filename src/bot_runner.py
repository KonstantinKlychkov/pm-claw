"""Entry point for the PM Claw Telegram bot."""

from __future__ import annotations

import sys

from dotenv import load_dotenv

from src.bot.bot import create_app


def main() -> None:
    """Load environment, create the bot application and start polling."""
    load_dotenv()
    try:
        app = create_app()
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)
    app.run_polling()


if __name__ == "__main__":
    main()
