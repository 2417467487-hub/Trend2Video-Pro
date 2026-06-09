"""Opportunity scoring facade."""

from __future__ import annotations

from typing import Any

from src.scoring.trend_scorer import score_topic as _score_topic


def score_topic(topic: dict[str, Any] | str, creator_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Score a normalized topic dictionary or a plain title."""
    if isinstance(topic, str):
        return _score_topic(topic, creator_profile=creator_profile)
    return _score_topic(
        title=topic.get("title", ""),
        url=topic.get("url", ""),
        platform=topic.get("platform", "B站"),
        style=topic.get("style", "科技资讯"),
        page_text=topic.get("description", ""),
        creator_profile=creator_profile,
    )


__all__ = ["score_topic"]
