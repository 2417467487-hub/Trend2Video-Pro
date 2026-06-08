"""Thumbnail copy generation."""

from __future__ import annotations


def generate_cover_copy(title: str) -> dict[str, str]:
    """Generate thumbnail title, subtitle, and keyword."""
    keyword = title.split()[0] if title.split() else title[:8]
    return {
        "headline": title[:18],
        "subtitle": "一分钟看懂机会",
        "keyword": keyword[:10],
    }
