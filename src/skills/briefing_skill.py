"""Daily briefing skill for PM Claw agent."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.skills.digest_skill import DigestSkill
from src.skills.idea_generator import IdeaGeneratorSkill

logger = logging.getLogger(__name__)


@dataclass
class BriefingSkill:
    """Aggregates news and ideas into a daily PM briefing.

    Args:
        feed_urls: RSS feed URLs passed to DigestSkill.
        idea_topic: Topic string passed to IdeaGeneratorSkill.
        action_items: Optional list of manual action items to include.
    """

    feed_urls: list[str]
    idea_topic: str
    action_items: list[str] = field(default_factory=list)
    _errors: list[str] = field(default_factory=list, init=False, repr=False)
    _sections: dict[str, str] = field(default_factory=dict, init=False, repr=False)

    def collect_news(self) -> str:
        """Fetches the news digest via DigestSkill and caches the result.

        Creates a DigestSkill instance with ``feed_urls``, calls
        ``generate_digest()``, stores the result in ``_sections["news"]``,
        and appends any errors from DigestSkill into ``_errors``.

        Returns:
            Formatted digest text returned by DigestSkill.
        """
        skill = DigestSkill(urls=self.feed_urls)
        text = skill.generate_digest()
        self._errors.extend(skill._errors)
        self._sections["news"] = text
        logger.debug("Collected news digest (%d chars)", len(text))
        return text

    def collect_ideas(self) -> str:
        """Fetches the ideas report via IdeaGeneratorSkill and caches the result.

        Creates an IdeaGeneratorSkill instance with ``idea_topic``, calls
        ``format_report()``, stores the result in ``_sections["ideas"]``,
        and appends any errors from IdeaGeneratorSkill into ``_errors``.

        Returns:
            Formatted ideas report text returned by IdeaGeneratorSkill.
        """
        skill = IdeaGeneratorSkill(topic=self.idea_topic)
        text = skill.format_report()
        self._errors.extend(skill._errors)
        self._sections["ideas"] = text
        logger.debug("Collected ideas report (%d chars)", len(text))
        return text

    def generate_briefing(self) -> str:
        """Generates the full daily briefing by collecting news and ideas.

        Calls ``collect_news()`` and ``collect_ideas()`` unconditionally,
        then delegates to ``_format_briefing_text`` to assemble the output.

        Returns:
            Formatted briefing string with all sections.
        """
        news = self.collect_news()
        ideas = self.collect_ideas()
        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        result = _format_briefing_text(date_str, news, ideas, self.action_items, self._errors)
        logger.debug("Generated briefing for date %s", date_str)
        return result

    def format_briefing(self) -> str:
        """Returns the briefing, generating it first if the cache is empty.

        If ``_sections`` is empty (i.e. neither ``collect_news`` nor
        ``collect_ideas`` has been called yet), delegates to
        ``generate_briefing()`` to populate the cache and build the output.
        Otherwise assembles the briefing from the cached sections directly.

        Returns:
            Formatted briefing string.
        """
        if not self._sections:
            return self.generate_briefing()

        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        news = self._sections.get("news", "")
        ideas = self._sections.get("ideas", "")
        return _format_briefing_text(date_str, news, ideas, self.action_items, self._errors)


def _format_briefing_text(
    date_str: str,
    news: str,
    ideas: str,
    action_items: list[str],
    errors: list[str],
) -> str:
    """Assembles the final briefing text from its constituent parts.

    Args:
        date_str: ISO date string (``YYYY-MM-DD``) for the briefing header.
        news: News digest text; shown verbatim or replaced by a fallback message.
        ideas: Ideas report text; shown verbatim or replaced by a fallback message.
        action_items: List of manual action item strings.
        errors: Accumulated error strings; section omitted when list is empty.

    Returns:
        Multi-section briefing string.
    """
    lines: list[str] = [
        "=== PM Daily Briefing ===",
        f"Date: {date_str}",
        "",
        "--- News Digest ---",
        news if news else "No news available.",
        "",
        "--- Ideas ---",
        ideas if ideas else "No ideas available.",
        "",
        "--- Action Items ---",
    ]

    if action_items:
        for item in action_items:
            lines.append(f"- {item}")
    else:
        lines.append("No action items.")

    if errors:
        lines.append("")
        lines.append("--- Errors ---")
        for error in errors:
            lines.append(error)

    return "\n".join(lines)
