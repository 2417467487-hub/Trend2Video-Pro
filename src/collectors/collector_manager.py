"""Collector orchestration and topic normalization."""

from __future__ import annotations

from typing import Any

from src.collectors.github_trending import collect_github_trending
from src.collectors.hackernews_collector import collect_hackernews
from src.collectors.producthunt_collector import collect_producthunt
from src.scoring.opportunity_scorer import score_topic


def collect_all_topics(limit: int = 20) -> list[dict[str, Any]]:
    """Collect topics from multiple sources, de-duplicate, and score."""
    raw_topics = [
        *collect_github_trending(limit=max(3, limit // 3)),
        *collect_hackernews(limit=max(3, limit // 3)),
        *collect_producthunt(limit=max(3, limit // 3)),
    ]
    seen: set[str] = set()
    topics: list[dict[str, Any]] = []
    for item in raw_topics:
        url = item.get("url") or f"manual://{item.get('title', '')}"
        key = url.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        topic = {
            "source": item.get("source", "unknown"),
            "title": item.get("title", "Untitled trend"),
            "url": url,
            "description": item.get("description", ""),
            "raw_score": float(item.get("stars_today") or item.get("points") or item.get("votes") or 0),
            "collected_at": item.get("collected_at"),
            "raw": item,
        }
        topic.update(score_topic(topic))
        topics.append(topic)
    topics.sort(key=lambda row: row.get("final_opportunity_score", 0), reverse=True)
    return topics[:limit]
