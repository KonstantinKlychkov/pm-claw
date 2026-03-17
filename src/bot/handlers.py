"""Telegram bot command handlers."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.config.settings import DEFAULT_FEED_URLS
from src.skills import SKILL_REGISTRY
from src.skills.briefing_skill import BriefingSkill
from src.skills.competitor_skill import CompetitorSkill
from src.skills.digest_skill import DigestSkill
from src.skills.idea_generator import IdeaGeneratorSkill

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4096


async def _send_long_message(update: Update, text: str) -> None:
    """Splits text into chunks and sends them sequentially."""
    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        await update.message.reply_text(text[i : i + MAX_MESSAGE_LENGTH])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start — welcome message with available commands."""
    lines = ["PM Claw Bot — your PM assistant.", "", "Available commands:"]
    for name, info in SKILL_REGISTRY.items():
        lines.append(f"/{name} — {info['description']}")
    lines.append("/help — show this message")
    await update.message.reply_text("\n".join(lines))


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /help — lists commands with usage examples."""
    lines = ["Commands:"]
    for info in SKILL_REGISTRY.values():
        lines.append(f"  {info['usage']}")
    lines.append("  /help — show this message")
    await update.message.reply_text("\n".join(lines))


async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /digest — collects RSS feed digest."""
    urls = DEFAULT_FEED_URLS
    if not urls:
        await update.message.reply_text(
            "No feed URLs configured. Set FEED_URLS in .env file."
        )
        return

    await update.message.reply_text("Collecting feeds...")
    skill = DigestSkill(urls=urls)
    result = skill.generate_digest()
    await _send_long_message(update, result)


async def cmd_ideas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /ideas <topic> — generates SCAMPER ideas."""
    topic = " ".join(context.args) if context.args else ""
    if not topic:
        await update.message.reply_text("Usage: /ideas <topic>")
        return

    skill = IdeaGeneratorSkill(topic=topic)
    result = skill.format_report()
    await _send_long_message(update, result)


async def cmd_competitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /competitor <product> — runs competitor analysis."""
    product = " ".join(context.args) if context.args else ""
    if not product:
        await update.message.reply_text("Usage: /competitor <product name>")
        return

    skill = CompetitorSkill(product_name=product)
    result = skill.format_report()
    await _send_long_message(update, result)


async def cmd_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /briefing <topic> — generates daily PM briefing."""
    topic = " ".join(context.args) if context.args else "product management"
    urls = DEFAULT_FEED_URLS

    if not urls:
        await update.message.reply_text(
            "No feed URLs configured. Set FEED_URLS in .env file."
        )
        return

    await update.message.reply_text("Generating briefing...")
    skill = BriefingSkill(feed_urls=urls, idea_topic=topic)
    result = skill.format_briefing()
    await _send_long_message(update, result)
