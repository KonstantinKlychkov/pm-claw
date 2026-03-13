"""RSS digest skill for PM Claw agent."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from urllib.parse import urlparse

import feedparser

logger = logging.getLogger(__name__)


@dataclass
class DigestSkill:
    """Collects and formats RSS feed digests.

    Args:
        urls: List of RSS feed URLs to process.
    """

    urls: list[str]
    _errors: list[str] = field(default_factory=list, init=False, repr=False)

    def validate_urls(self) -> list[str]:
        """Checks that all URLs start with http:// or https://.

        Returns:
            List of invalid URLs. Empty list means all URLs are valid.
        """
        invalid: list[str] = []
        for url in self.urls:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                invalid.append(url)
        return invalid

    def fetch_feed(self, url: str) -> list[dict]:
        """Parses a single RSS feed and returns its entries.

        Args:
            url: RSS feed URL.

        Returns:
            List of dicts with keys: title, link, summary, published.
        """
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            logger.error("Failed to fetch feed %s: %s", url, exc)
            self._errors.append(f"Error fetching {url}: {exc}")
            return []

        if feed.bozo and not feed.entries:
            msg = str(getattr(feed, "bozo_exception", "unknown error"))
            logger.warning("Bad feed %s: %s", url, msg)
            self._errors.append(f"Bad feed {url}: {msg}")
            return []

        entries: list[dict] = []
        for entry in feed.entries:
            entries.append(
                {
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "summary": _clean_summary(
                        entry.get("summary", "")
                    ),
                    "published": entry.get("published", ""),
                }
            )
        return entries

    def generate_digest(self) -> str:
        """Fetches all feeds and formats a readable digest.

        Validates URLs first, skips invalid ones, collects entries
        from all valid feeds, and returns formatted text.

        Returns:
            Formatted digest string with headers and links.
        """
        invalid = self.validate_urls()
        if invalid:
            for url in invalid:
                self._errors.append(f"Invalid URL skipped: {url}")

        valid_urls = [u for u in self.urls if u not in invalid]
        if not valid_urls:
            return "No valid URLs provided."

        all_entries: list[tuple[str, list[dict]]] = []
        for url in valid_urls:
            entries = self.fetch_feed(url)
            if entries:
                feed_title = _extract_feed_title(url, entries)
                all_entries.append((feed_title, entries))

        if not all_entries:
            error_block = "\n".join(self._errors) if self._errors else ""
            return f"No entries found in any feed.\n{error_block}".strip()

        return _format_digest(all_entries)


def _clean_summary(raw: str, max_length: int = 200) -> str:
    """Strips HTML tags and truncates summary text."""
    import re

    text = re.sub(r"<[^>]+>", "", raw).strip()
    if len(text) > max_length:
        text = text[:max_length].rsplit(" ", 1)[0] + "..."
    return text


def _extract_feed_title(url: str, entries: list[dict]) -> str:
    """Tries to derive a human-readable feed title from the URL."""
    parsed = urlparse(url)
    return parsed.netloc or url


def _format_digest(feeds: list[tuple[str, list[dict]]]) -> str:
    """Builds the final digest text from collected feed entries."""
    lines: list[str] = []
    for feed_title, entries in feeds:
        lines.append(f"== {feed_title} ==")
        for entry in entries:
            title = entry["title"]
            link = entry["link"]
            summary = entry["summary"]
            published = entry["published"]

            lines.append(f"  - {title}")
            if published:
                lines.append(f"    {published}")
            if summary:
                lines.append(f"    {summary}")
            if link:
                lines.append(f"    {link}")
            lines.append("")
    return "\n".join(lines).strip()
