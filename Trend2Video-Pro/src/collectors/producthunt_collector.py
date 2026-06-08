"""Product Hunt collector placeholder for MVP."""

from __future__ import annotations


def collect_producthunt(limit: int = 10) -> list[dict[str, str]]:
    """Return lightweight Product Hunt seed items."""
    return [
        {
            "title": f"Product Hunt 热门产品 #{idx + 1}",
            "url": "https://www.producthunt.com/",
            "source": "producthunt",
        }
        for idx in range(limit)
    ]
