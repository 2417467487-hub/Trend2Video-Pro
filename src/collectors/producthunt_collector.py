"""Product Hunt collector placeholder with API-ready mock fallback."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any

import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)


def _mock_items(limit: int) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    seeds = [
        ("ClipPilot AI", "AI assistant that turns product updates into short videos"),
        ("LaunchBrief", "Summarize launches and create creator-ready content briefs"),
        ("CreatorOps", "Automation toolkit for solo creator publishing workflows"),
    ]
    return [
        {
            "title": title,
            "url": f"https://www.producthunt.com/posts/{title.lower().replace(' ', '-')}",
            "description": description,
            "source": "producthunt",
            "votes": 120 - idx * 18,
            "collected_at": now,
        }
        for idx, (title, description) in enumerate(seeds[:limit])
    ]


def collect_producthunt(limit: int = 10) -> list[dict[str, Any]]:
    """Collect Product Hunt launches.

    Product Hunt GraphQL requires an API token. If it is missing or fails,
    deterministic mock launches are returned so the demo remains runnable.
    """
    token = os.getenv("PRODUCTHUNT_API_KEY", "")
    if not token:
        return _mock_items(limit)
    try:
        query = """
        query TodayPosts($first: Int!) {
          posts(first: $first, order: VOTES) {
            edges {
              node { name tagline url votesCount createdAt }
            }
          }
        }
        """
        response = requests.post(
            "https://api.producthunt.com/v2/api/graphql",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": query, "variables": {"first": limit}},
            timeout=20,
        )
        response.raise_for_status()
        now = datetime.now(timezone.utc).isoformat()
        edges = response.json().get("data", {}).get("posts", {}).get("edges", [])
        return [
            {
                "title": edge["node"]["name"],
                "url": edge["node"]["url"],
                "description": edge["node"].get("tagline", ""),
                "source": "producthunt",
                "votes": edge["node"].get("votesCount", 0),
                "collected_at": now,
            }
            for edge in edges
        ] or _mock_items(limit)
    except Exception as exc:
        logger.warning("Product Hunt collector failed, using mock data: %s", exc)
        return _mock_items(limit)
