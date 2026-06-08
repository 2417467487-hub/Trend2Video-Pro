"""GitHub Trending collector placeholder for MVP."""

from __future__ import annotations


def collect_github_trending(language: str = "python", limit: int = 10) -> list[dict[str, str]]:
    """Return lightweight GitHub Trending seed items.

    The MVP focuses on user-supplied trends; this function keeps the future
    collector contract executable without depending on page layout scraping.
    """
    return [
        {
            "title": f"GitHub Trending {language} 项目 #{idx + 1}",
            "url": "https://github.com/trending",
            "source": "github",
        }
        for idx in range(limit)
    ]
