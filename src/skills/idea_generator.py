"""SCAMPER idea generation skill for PM Claw agent."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

SCAMPER_PROMPTS: dict[str, str] = {
    "Substitute": (
        "What components, materials, or processes in '{topic}'"
        " can be replaced with something else?"
    ),
    "Combine": (
        "What ideas, features, or processes can be combined"
        " with '{topic}' to create something new?"
    ),
    "Adapt": (
        "What existing solutions or approaches can be adapted"
        " to solve '{topic}' differently?"
    ),
    "Modify": (
        "What can be magnified, minimized, or otherwise modified"
        " in '{topic}' to improve it?"
    ),
    "Put to other use": (
        "How can '{topic}' or its components be used"
        " for a completely different purpose?"
    ),
    "Eliminate": (
        "What can be removed or simplified in '{topic}'"
        " without losing core value?"
    ),
    "Reverse": (
        "What happens if you reverse, flip, or rearrange"
        " the assumptions in '{topic}'?"
    ),
}


@dataclass
class IdeaGeneratorSkill:
    """Generates product ideas using the SCAMPER creative framework.

    Args:
        topic: The problem or topic to brainstorm about.
    """

    topic: str
    _ideas: dict[str, str] = field(default_factory=dict, init=False, repr=False)
    _errors: list[str] = field(default_factory=list, init=False, repr=False)

    def generate_scamper_ideas(self) -> dict[str, str]:
        """Generates one idea-prompt for each SCAMPER category.

        Resets ``_ideas`` on each call. Errors in ``_errors`` accumulate
        intentionally across calls (consistent with DigestSkill).

        Returns:
            Dict mapping category name to generated idea prompt.
            Empty dict if topic is invalid.
        """
        self._ideas = {}
        topic = self.topic.strip()
        if not topic:
            self._errors.append("Topic cannot be empty.")
            return {}

        self._ideas = {
            category: prompt.format(topic=topic)
            for category, prompt in SCAMPER_PROMPTS.items()
        }
        return dict(self._ideas)

    def save_to_markdown(
        self,
        output_dir: str | Path = "docs/ideas",
        base_dir: str | Path | None = None,
    ) -> str:
        """Saves generated ideas to a markdown file.

        Creates the output directory if it does not exist.
        Calls generate_scamper_ideas() automatically if ideas
        have not been generated yet.

        Args:
            output_dir: Directory to save the markdown file.
            base_dir: Allowed base directory. If provided, output_dir
                must resolve inside it; otherwise the call is rejected.

        Returns:
            Path to the created file, or empty string on failure.
        """
        if not self._ideas:
            self.generate_scamper_ideas()
        if not self._ideas:
            return ""

        dir_path = Path(output_dir).resolve()
        if base_dir is not None:
            allowed = Path(base_dir).resolve()
            if not dir_path.is_relative_to(allowed):
                msg = f"output_dir '{output_dir}' is outside allowed base '{base_dir}'"
                logger.error(msg)
                self._errors.append(msg)
                return ""
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            logger.error("Cannot create directory %s: %s", output_dir, exc)
            self._errors.append(f"Cannot create directory {output_dir}: {exc}")
            return ""

        slug = _slugify(self.topic)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{slug}_{timestamp}.md"
        file_path = dir_path / filename

        content = _format_markdown(self.topic.strip(), self._ideas)
        try:
            file_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            logger.error("Cannot write file %s: %s", file_path, exc)
            self._errors.append(f"Cannot write file {file_path}: {exc}")
            return ""

        return str(file_path)

    def format_report(self) -> str:
        """Formats generated ideas as a readable plain-text report.

        Calls generate_scamper_ideas() automatically if ideas
        have not been generated yet.

        Returns:
            Formatted report string, or error message if topic is invalid.
        """
        if not self._ideas:
            self.generate_scamper_ideas()
        if not self._ideas:
            error_block = "\n".join(self._errors) if self._errors else ""
            return f"No ideas generated.\n{error_block}".strip()

        return _format_report(self.topic.strip(), self._ideas)


def _slugify(text: str, max_length: int = 50) -> str:
    """Converts text to a filesystem-safe slug.

    Args:
        text: Input text.
        max_length: Maximum slug length.

    Returns:
        Lowercased, hyphen-separated slug.
    """
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_length].rstrip("-")


def _format_markdown(topic: str, ideas: dict[str, str]) -> str:
    """Builds a full markdown document for the generated ideas.

    Args:
        topic: The product topic string.
        ideas: Mapping of SCAMPER category to generated prompt.

    Returns:
        Markdown-formatted string with headers, date, and idea sections.
    """
    date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = [
        f"# Idea Generation: {topic}",
        "",
        f"**Date:** {date_str}",
        "**Framework:** SCAMPER",
        "",
        "---",
    ]
    for category, idea in ideas.items():
        lines.append("")
        lines.append(f"## {category}")
        lines.append("")
        lines.append(f"**Prompt:** {idea}")
        lines.append("")
    return "\n".join(lines)


def _format_report(topic: str, ideas: dict[str, str]) -> str:
    """Builds a plain-text report from generated ideas.

    Args:
        topic: The product topic string.
        ideas: Mapping of SCAMPER category to generated prompt.

    Returns:
        Plain-text formatted string with category labels and prompts.
    """
    lines: list[str] = [f"=== SCAMPER Ideas: {topic} ===", ""]
    for category, idea in ideas.items():
        lines.append(f"[{category}]")
        lines.append(f"  {idea}")
        lines.append("")
    return "\n".join(lines).strip()
