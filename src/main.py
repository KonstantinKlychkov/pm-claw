"""PM Claw — персональный ассистент продакт-менеджера."""

import logging

from src.bot.app import create_app


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    try:
        app = create_app()
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    app.run_polling()


if __name__ == "__main__":
    main()
