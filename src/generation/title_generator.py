"""Video title generation."""

from __future__ import annotations


def generate_titles(topic: str, platform: str) -> list[str]:
    """Generate simple platform-aware title candidates."""
    return [
        f"{topic}，普通人该怎么看？",
        f"一分钟看懂：{topic}",
        f"{platform}创作者必看：{topic}",
    ]
