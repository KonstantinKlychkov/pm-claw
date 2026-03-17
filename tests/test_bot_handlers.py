"""Tests for src/bot/handlers.py — Telegram command handlers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot.handlers import (
    MAX_MESSAGE_LENGTH,
    _send_long_message,
    cmd_briefing,
    cmd_competitor,
    cmd_digest,
    cmd_help,
    cmd_ideas,
    cmd_start,
)
from src.skills import SKILL_REGISTRY


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def update() -> MagicMock:
    """Fake telegram.Update with an AsyncMock reply_text."""
    mock = MagicMock()
    mock.message.reply_text = AsyncMock()
    return mock


@pytest.fixture
def context() -> MagicMock:
    """Fake ContextTypes.DEFAULT_TYPE with no args by default."""
    mock = MagicMock()
    mock.args = []
    return mock


# ---------------------------------------------------------------------------
# _send_long_message — splitting behaviour
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_long_message_short_text_sends_once(update: MagicMock) -> None:
    """_send_long_message sends a single chunk when text is within the limit."""
    await _send_long_message(update, "Hello, world!")
    update.message.reply_text.assert_awaited_once_with("Hello, world!")


@pytest.mark.asyncio
async def test_send_long_message_exact_limit_sends_once(update: MagicMock) -> None:
    """_send_long_message sends one chunk for text exactly MAX_MESSAGE_LENGTH chars."""
    text = "x" * MAX_MESSAGE_LENGTH
    await _send_long_message(update, text)
    assert update.message.reply_text.await_count == 1


@pytest.mark.asyncio
async def test_send_long_message_over_limit_splits_into_two_chunks(
    update: MagicMock,
) -> None:
    """_send_long_message splits text exceeding the limit into two calls."""
    text = "y" * (MAX_MESSAGE_LENGTH + 1)
    await _send_long_message(update, text)
    assert update.message.reply_text.await_count == 2


@pytest.mark.asyncio
async def test_send_long_message_three_chunks_for_triple_limit(update: MagicMock) -> None:
    """_send_long_message issues three reply_text calls for 3x the limit."""
    text = "z" * (MAX_MESSAGE_LENGTH * 3)
    await _send_long_message(update, text)
    assert update.message.reply_text.await_count == 3


@pytest.mark.asyncio
async def test_send_long_message_empty_text_sends_no_messages(update: MagicMock) -> None:
    """_send_long_message sends nothing when given an empty string."""
    await _send_long_message(update, "")
    update.message.reply_text.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_long_message_chunks_preserve_full_content(update: MagicMock) -> None:
    """All chunks concatenated reconstruct the original text exactly."""
    text = "a" * (MAX_MESSAGE_LENGTH + 500)
    await _send_long_message(update, text)
    reconstructed = "".join(
        call.args[0] for call in update.message.reply_text.await_args_list
    )
    assert reconstructed == text


# ---------------------------------------------------------------------------
# cmd_start
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_start_replies_once(update: MagicMock, context: MagicMock) -> None:
    """cmd_start sends exactly one message."""
    await cmd_start(update, context)
    update.message.reply_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_cmd_start_reply_contains_bot_name(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_start reply mentions 'PM Claw Bot'."""
    await cmd_start(update, context)
    text = update.message.reply_text.call_args.args[0]
    assert "PM Claw Bot" in text


@pytest.mark.asyncio
async def test_cmd_start_reply_lists_all_registry_commands(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_start reply contains every skill name from SKILL_REGISTRY."""
    await cmd_start(update, context)
    text = update.message.reply_text.call_args.args[0]
    for name in SKILL_REGISTRY:
        assert f"/{name}" in text


@pytest.mark.asyncio
async def test_cmd_start_reply_contains_help_command(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_start reply mentions the /help command."""
    await cmd_start(update, context)
    text = update.message.reply_text.call_args.args[0]
    assert "/help" in text


# ---------------------------------------------------------------------------
# cmd_help
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_help_replies_once(update: MagicMock, context: MagicMock) -> None:
    """cmd_help sends exactly one message."""
    await cmd_help(update, context)
    update.message.reply_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_cmd_help_reply_contains_all_usage_strings(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_help reply contains the usage string for every registered skill."""
    await cmd_help(update, context)
    text = update.message.reply_text.call_args.args[0]
    for info in SKILL_REGISTRY.values():
        assert info["usage"] in text


@pytest.mark.asyncio
async def test_cmd_help_reply_mentions_help_command(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_help reply mentions /help itself."""
    await cmd_help(update, context)
    text = update.message.reply_text.call_args.args[0]
    assert "/help" in text


# ---------------------------------------------------------------------------
# cmd_digest — no feed URLs configured
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_digest_with_no_feed_urls_replies_with_config_hint(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_digest replies with a configuration hint when DEFAULT_FEED_URLS is empty."""
    with patch("src.bot.handlers.DEFAULT_FEED_URLS", []):
        await cmd_digest(update, context)

    text = update.message.reply_text.call_args.args[0]
    assert "FEED_URLS" in text


@pytest.mark.asyncio
async def test_cmd_digest_with_no_feed_urls_does_not_call_digest_skill(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_digest does not instantiate DigestSkill when no URLs are configured."""
    with (
        patch("src.bot.handlers.DEFAULT_FEED_URLS", []),
        patch("src.bot.handlers.DigestSkill") as mock_skill_cls,
    ):
        await cmd_digest(update, context)

    mock_skill_cls.assert_not_called()


# ---------------------------------------------------------------------------
# cmd_digest — happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_digest_with_feed_urls_sends_collecting_message(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_digest sends an interim 'Collecting feeds...' message."""
    fake_urls = ["https://example.com/rss"]
    with (
        patch("src.bot.handlers.DEFAULT_FEED_URLS", fake_urls),
        patch("src.bot.handlers.DigestSkill") as mock_skill_cls,
    ):
        mock_skill_cls.return_value.generate_digest.return_value = "digest content"
        await cmd_digest(update, context)

    calls = [c.args[0] for c in update.message.reply_text.await_args_list]
    assert any("Collecting" in c for c in calls)


@pytest.mark.asyncio
async def test_cmd_digest_with_feed_urls_sends_digest_result(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_digest sends the DigestSkill output after the interim message."""
    fake_urls = ["https://example.com/rss"]
    with (
        patch("src.bot.handlers.DEFAULT_FEED_URLS", fake_urls),
        patch("src.bot.handlers.DigestSkill") as mock_skill_cls,
    ):
        mock_skill_cls.return_value.generate_digest.return_value = "digest content"
        await cmd_digest(update, context)

    calls = [c.args[0] for c in update.message.reply_text.await_args_list]
    assert any("digest content" in c for c in calls)


@pytest.mark.asyncio
async def test_cmd_digest_instantiates_skill_with_correct_urls(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_digest passes DEFAULT_FEED_URLS to DigestSkill constructor."""
    fake_urls = ["https://example.com/rss", "https://blog.test/feed"]
    with (
        patch("src.bot.handlers.DEFAULT_FEED_URLS", fake_urls),
        patch("src.bot.handlers.DigestSkill") as mock_skill_cls,
    ):
        mock_skill_cls.return_value.generate_digest.return_value = "ok"
        await cmd_digest(update, context)

    mock_skill_cls.assert_called_once_with(urls=fake_urls)


# ---------------------------------------------------------------------------
# cmd_ideas — missing topic
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_ideas_without_args_replies_with_usage(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_ideas replies with usage hint when no topic is provided."""
    context.args = []
    await cmd_ideas(update, context)

    text = update.message.reply_text.call_args.args[0]
    assert "Usage" in text or "usage" in text


@pytest.mark.asyncio
async def test_cmd_ideas_without_args_does_not_call_skill(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_ideas does not call IdeaGeneratorSkill when topic is absent."""
    context.args = []
    with patch("src.bot.handlers.IdeaGeneratorSkill") as mock_skill_cls:
        await cmd_ideas(update, context)
    mock_skill_cls.assert_not_called()


# ---------------------------------------------------------------------------
# cmd_ideas — happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_ideas_with_args_passes_topic_to_skill(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_ideas joins context.args and passes the result as topic."""
    context.args = ["remote", "work"]
    with patch("src.bot.handlers.IdeaGeneratorSkill") as mock_skill_cls:
        mock_skill_cls.return_value.format_report.return_value = "ideas report"
        await cmd_ideas(update, context)

    mock_skill_cls.assert_called_once_with(topic="remote work")


@pytest.mark.asyncio
async def test_cmd_ideas_with_args_sends_skill_output(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_ideas sends IdeaGeneratorSkill.format_report() output to the user."""
    context.args = ["productivity"]
    with patch("src.bot.handlers.IdeaGeneratorSkill") as mock_skill_cls:
        mock_skill_cls.return_value.format_report.return_value = "ideas report"
        await cmd_ideas(update, context)

    calls = [c.args[0] for c in update.message.reply_text.await_args_list]
    assert any("ideas report" in c for c in calls)


# ---------------------------------------------------------------------------
# cmd_competitor — missing product name
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_competitor_without_args_replies_with_usage(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_competitor replies with usage hint when no product name is provided."""
    context.args = []
    await cmd_competitor(update, context)

    text = update.message.reply_text.call_args.args[0]
    assert "Usage" in text or "usage" in text


@pytest.mark.asyncio
async def test_cmd_competitor_without_args_does_not_call_skill(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_competitor does not call CompetitorSkill when product name is absent."""
    context.args = []
    with patch("src.bot.handlers.CompetitorSkill") as mock_skill_cls:
        await cmd_competitor(update, context)
    mock_skill_cls.assert_not_called()


# ---------------------------------------------------------------------------
# cmd_competitor — happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_competitor_with_args_passes_product_to_skill(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_competitor joins context.args and passes the result as product_name."""
    context.args = ["Notion", "AI"]
    with patch("src.bot.handlers.CompetitorSkill") as mock_skill_cls:
        mock_skill_cls.return_value.format_report.return_value = "competitor report"
        await cmd_competitor(update, context)

    mock_skill_cls.assert_called_once_with(product_name="Notion AI")


@pytest.mark.asyncio
async def test_cmd_competitor_with_args_sends_skill_output(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_competitor sends CompetitorSkill.format_report() output to the user."""
    context.args = ["Slack"]
    with patch("src.bot.handlers.CompetitorSkill") as mock_skill_cls:
        mock_skill_cls.return_value.format_report.return_value = "competitor report"
        await cmd_competitor(update, context)

    calls = [c.args[0] for c in update.message.reply_text.await_args_list]
    assert any("competitor report" in c for c in calls)


# ---------------------------------------------------------------------------
# cmd_briefing — no feed URLs configured
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_briefing_with_no_feed_urls_replies_with_config_hint(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_briefing replies with a configuration hint when no URLs are configured."""
    context.args = []
    with patch("src.bot.handlers.DEFAULT_FEED_URLS", []):
        await cmd_briefing(update, context)

    text = update.message.reply_text.call_args.args[0]
    assert "FEED_URLS" in text


@pytest.mark.asyncio
async def test_cmd_briefing_with_no_feed_urls_does_not_call_briefing_skill(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_briefing does not instantiate BriefingSkill when no URLs are configured."""
    context.args = []
    with (
        patch("src.bot.handlers.DEFAULT_FEED_URLS", []),
        patch("src.bot.handlers.BriefingSkill") as mock_skill_cls,
    ):
        await cmd_briefing(update, context)

    mock_skill_cls.assert_not_called()


# ---------------------------------------------------------------------------
# cmd_briefing — happy path with explicit topic
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_briefing_with_args_passes_topic_to_skill(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_briefing joins context.args and passes it as idea_topic."""
    context.args = ["AI", "tools"]
    fake_urls = ["https://example.com/rss"]
    with (
        patch("src.bot.handlers.DEFAULT_FEED_URLS", fake_urls),
        patch("src.bot.handlers.BriefingSkill") as mock_skill_cls,
    ):
        mock_skill_cls.return_value.format_briefing.return_value = "briefing text"
        await cmd_briefing(update, context)

    mock_skill_cls.assert_called_once_with(feed_urls=fake_urls, idea_topic="AI tools")


@pytest.mark.asyncio
async def test_cmd_briefing_with_args_sends_skill_output(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_briefing sends BriefingSkill.format_briefing() output to the user."""
    context.args = ["product"]
    fake_urls = ["https://example.com/rss"]
    with (
        patch("src.bot.handlers.DEFAULT_FEED_URLS", fake_urls),
        patch("src.bot.handlers.BriefingSkill") as mock_skill_cls,
    ):
        mock_skill_cls.return_value.format_briefing.return_value = "briefing text"
        await cmd_briefing(update, context)

    calls = [c.args[0] for c in update.message.reply_text.await_args_list]
    assert any("briefing text" in c for c in calls)


# ---------------------------------------------------------------------------
# cmd_briefing — default topic when no args
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_briefing_without_args_uses_default_topic(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_briefing defaults the topic to 'product management' when no args given."""
    context.args = []
    fake_urls = ["https://example.com/rss"]
    with (
        patch("src.bot.handlers.DEFAULT_FEED_URLS", fake_urls),
        patch("src.bot.handlers.BriefingSkill") as mock_skill_cls,
    ):
        mock_skill_cls.return_value.format_briefing.return_value = "briefing text"
        await cmd_briefing(update, context)

    mock_skill_cls.assert_called_once_with(
        feed_urls=fake_urls, idea_topic="product management"
    )


# ---------------------------------------------------------------------------
# cmd_briefing — interim message
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cmd_briefing_with_feed_urls_sends_generating_message(
    update: MagicMock, context: MagicMock
) -> None:
    """cmd_briefing sends an interim 'Generating briefing...' message."""
    context.args = []
    fake_urls = ["https://example.com/rss"]
    with (
        patch("src.bot.handlers.DEFAULT_FEED_URLS", fake_urls),
        patch("src.bot.handlers.BriefingSkill") as mock_skill_cls,
    ):
        mock_skill_cls.return_value.format_briefing.return_value = "briefing text"
        await cmd_briefing(update, context)

    calls = [c.args[0] for c in update.message.reply_text.await_args_list]
    assert any("Generating" in c for c in calls)
