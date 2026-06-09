"""Hacker News collector using the Algolia API with mock fallback."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)


def _mock_items(limit: int) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    seeds = [
        ("AI agents are moving into browser workflows", "https://news.ycombinator.com/item?id=1", 420, 128),
        ("Open-source tools for automated video creation", "https://news.ycombinator.com/item?id=2", 260, 72),
        ("Local-first creator automation pipelines", "https://news.ycombinator.com/item?id=3", 180, 41),
    ]
    return [
        {
            "title": title,
            "url": url,
            "points": points,
            "num_comments": comments,
            "created_at": now,
            "source": "hackernews",
            "collected_at": now,
            "description": f"{points} points and {comments} comments on Hacker News.",
        }
        for title, url, points, comments in seeds[:limit]
    ]


def collect_hackernews(limit: int = 10) -> list[dict[str, Any]]:
    """Collect recent HN stories about AI/tools/automation."""
    endpoint = "https://hn.algolia.com/api/v1/search_by_date"
    params = {"query": "AI OR agent OR automation OR video", "tags": "story", "hitsPerPage": limit}
    try:
        response = requests.get(endpoint, params=params, timeout=15)
        response.raise_for_status()
        now = datetime.now(timezone.utc).isoformat()
        items: list[dict[str, Any]] = []
        for hit in response.json().get("hits", [])[:limit]:
            title = hit.get("title") or hit.get("story_title") or "Untitled HN story"
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            items.append(
                {
                    "title": title,
                    "url": url,
                    "points": hit.get("points") or 0,
                    "num_comments": hit.get("num_comments") or 0,
                    "created_at": hit.get("created_at") or now,
                    "source": "hackernews",
                    "collected_at": now,
                    "description": f"{hit.get('points') or 0} points, {hit.get('num_comments') or 0} comments.",
                }
            )
        return items or _mock_items(limit)
    except Exception as exc:
        logger.warning("Hacker News collector failed, using mock data: %s", exc)
        return _mock_items(limit)
