"""Competitor analysis skill for PM Claw agent."""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CompetitorSkill:
    """Performs mini competitor analysis for a given product.

    Args:
        product_name: Name of the competitor product to analyse.
    """

    product_name: str
    _errors: list[str] = field(default_factory=list, init=False, repr=False)
    _analysis: dict | None = field(default=None, init=False, repr=False)

    def analyze(self) -> dict:
        """Validates product_name and builds a structured analysis dict.

        Caches the result in ``_analysis``. Returns an empty dict and
        appends an error message when product_name is blank.

        Returns:
            Dict with keys: product_name, description, key_features,
            strengths, weaknesses, pricing_model.
            Empty dict if product_name is invalid.
        """
        name = self.product_name.strip()
        if not name:
            self._errors.append("Product name cannot be empty.")
            logger.warning("analyze() called with empty product_name")
            return {}

        self._analysis = {
            "product_name": name,
            "description": f"Overview of {name} — add details from research.",
            "key_features": [
                f"Feature 1 of {name}",
                f"Feature 2 of {name}",
                f"Feature 3 of {name}",
            ],
            "strengths": [
                f"Strength 1 of {name}",
                f"Strength 2 of {name}",
            ],
            "weaknesses": [
                f"Weakness 1 of {name}",
                f"Weakness 2 of {name}",
            ],
            "pricing_model": f"Pricing model for {name} — add details from research.",
        }
        logger.debug("analyze() completed for product '%s'", name)
        return copy.deepcopy(self._analysis)

    def format_report(self) -> str:
        """Formats the analysis as a plain-text report.

        Calls analyze() automatically if no cached result exists.

        Returns:
            Formatted plain-text report string, or an error message
            when product_name is invalid.
        """
        if self._analysis is None:
            self.analyze()
        if not self._analysis:
            error_block = "\n".join(self._errors) if self._errors else ""
            return f"No analysis available.\n{error_block}".strip()

        return _format_analysis_report(self._analysis)

    def compare(self, other: "CompetitorSkill") -> str:
        """Compares this skill's analysis with another's side by side.

        Auto-analyzes either instance if not yet cached. Returns an error
        message only when analysis fails (e.g. empty product name).

        Args:
            other: Another CompetitorSkill instance to compare against.

        Returns:
            Formatted comparison text, or an error message if either
            analysis is unavailable after auto-analyze.
        """
        if self._analysis is None:
            self.analyze()
        if other._analysis is None:
            other.analyze()

        if not self._analysis:
            msg = f"Analysis not available for '{self.product_name}'."
            logger.warning(msg)
            return f"Error: {msg}"
        if not other._analysis:
            msg = f"Analysis not available for '{other.product_name}'."
            logger.warning(msg)
            return f"Error: {msg}"

        return _format_comparison(self._analysis, other._analysis)


def _format_analysis_report(analysis: dict) -> str:
    """Builds the plain-text output for a single competitor analysis.

    Args:
        analysis: Dict produced by CompetitorSkill.analyze().

    Returns:
        Plain-text formatted report string.
    """
    name = analysis["product_name"]
    features = "\n".join(f"  - {f}" for f in analysis["key_features"])
    strengths = "\n".join(f"  + {s}" for s in analysis["strengths"])
    weaknesses = "\n".join(f"  - {w}" for w in analysis["weaknesses"])
    lines: list[str] = [
        f"=== Competitor Analysis: {name} ===",
        "",
        "[Description]",
        f"  {analysis['description']}",
        "",
        "[Key Features]",
        features,
        "",
        "[Strengths]",
        strengths,
        "",
        "[Weaknesses]",
        weaknesses,
        "",
        "[Pricing Model]",
        f"  {analysis['pricing_model']}",
    ]
    return "\n".join(lines).strip()


def _format_comparison(analysis_a: dict, analysis_b: dict) -> str:
    """Builds a side-by-side plain-text comparison of two analyses.

    Args:
        analysis_a: Dict produced by CompetitorSkill.analyze() for product A.
        analysis_b: Dict produced by CompetitorSkill.analyze() for product B.

    Returns:
        Plain-text formatted comparison string.
    """
    name_a = analysis_a["product_name"]
    name_b = analysis_b["product_name"]

    def _bullet(items: list[str], prefix: str) -> str:
        return "\n".join(f"  {prefix} {item}" for item in items)

    lines: list[str] = [
        f"=== Comparison: {name_a} vs {name_b} ===",
        "",
        f"[Description: {name_a}]",
        f"  {analysis_a['description']}",
        "",
        f"[Description: {name_b}]",
        f"  {analysis_b['description']}",
        "",
        f"[Key Features: {name_a}]",
        _bullet(analysis_a["key_features"], "-"),
        "",
        f"[Key Features: {name_b}]",
        _bullet(analysis_b["key_features"], "-"),
        "",
        f"[Strengths: {name_a}]",
        _bullet(analysis_a["strengths"], "+"),
        "",
        f"[Strengths: {name_b}]",
        _bullet(analysis_b["strengths"], "+"),
        "",
        f"[Weaknesses: {name_a}]",
        _bullet(analysis_a["weaknesses"], "-"),
        "",
        f"[Weaknesses: {name_b}]",
        _bullet(analysis_b["weaknesses"], "-"),
        "",
        f"[Pricing: {name_a}]",
        f"  {analysis_a['pricing_model']}",
        "",
        f"[Pricing: {name_b}]",
        f"  {analysis_b['pricing_model']}",
    ]
    return "\n".join(lines).strip()
