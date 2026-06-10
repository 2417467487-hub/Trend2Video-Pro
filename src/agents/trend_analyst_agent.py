"""Trend analyst agent."""

from __future__ import annotations

from typing import Any

from src.scoring.opportunity_scorer import score_topic


def analyze_trend(topic: dict[str, Any], creator_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Score and annotate a topic."""
    scored = dict(topic)
    scored.update(score_topic(scored, creator_profile=creator_profile))
    return scored
