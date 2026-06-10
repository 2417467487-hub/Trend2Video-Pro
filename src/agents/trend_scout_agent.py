"""Trend scout agent."""

from __future__ import annotations

from typing import Any

from src.collectors.collector_manager import collect_all_topics


def scout_trends(seed_topic: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    """Return candidate trends from a seed topic or collectors."""
    if seed_topic:
        return [{"title": seed_topic, "url": "", "description": "Manual seed topic", "source": "manual"}]
    return collect_all_topics(limit=limit)
