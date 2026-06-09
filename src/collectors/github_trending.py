"""GitHub Trending collector with mock fallback."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from src.utils.logger import get_logger

logger = get_logger(__name__)


def _mock_items(language: str, limit: int) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    seeds = [
        ("browser-use agent framework", "AI Agent browser automation toolkit", 38200, 4200, 830),
        ("open-source video generator", "Python pipeline for automated short video production", 12800, 980, 310),
        ("local-first AI workflow", "Run LLM content workflows locally with mock fallback", 9200, 640, 180),
    ]
    return [
        {
            "title": title,
            "url": f"https://github.com/example/{re.sub(r'\\s+', '-', title)}",
            "description": description,
            "language": language,
            "stars": stars,
            "forks": forks,
            "stars_today": stars_today,
            "source": "github",
            "collected_at": now,
        }
        for title, description, stars, forks, stars_today in seeds[:limit]
    ]


def collect_github_trending(language: str = "python", limit: int = 10) -> list[dict[str, Any]]:
    """Scrape GitHub Trending and return normalized topics.

    Network or layout failures return deterministic mock data.
    """
    now = datetime.now(timezone.utc).isoformat()
    url = f"https://github.com/trending/{language}?since=daily"
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Trend2Video-Pro/0.2"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items: list[dict[str, Any]] = []
        for article in soup.select("article.Box-row")[:limit]:
            heading = article.select_one("h2 a")
            if not heading:
                continue
            repo_path = " ".join(heading.get_text(" ", strip=True).split()).replace(" / ", "/")
            repo_url = "https://github.com" + heading.get("href", "")
            description_node = article.select_one("p")
            stars_node = article.select_one("a[href$='/stargazers']")
            forks_node = article.select_one("a[href$='/forks']")
            stars_today_node = article.find(string=re.compile("stars today"))
            lang_node = article.select_one("[itemprop='programmingLanguage']")
            items.append(
                {
                    "title": repo_path,
                    "url": repo_url,
                    "description": description_node.get_text(" ", strip=True) if description_node else "",
                    "language": lang_node.get_text(strip=True) if lang_node else language,
                    "stars": _parse_number(stars_node.get_text(strip=True) if stars_node else "0"),
                    "forks": _parse_number(forks_node.get_text(strip=True) if forks_node else "0"),
                    "stars_today": _parse_number(str(stars_today_node or "0")),
                    "source": "github",
                    "collected_at": now,
                }
            )
        return items or _mock_items(language, limit)
    except Exception as exc:
        logger.warning("GitHub Trending collector failed, using mock data: %s", exc)
        return _mock_items(language, limit)


def _parse_number(value: str) -> int:
    cleaned = value.replace(",", "")
    match = re.search(r"\d+", cleaned)
    return int(match.group(0)) if match else 0
