"""Webpage extraction and screenshot capture."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

from config.settings import settings
from src.utils.file_utils import slugify, write_json
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def _capture_with_playwright(url: str, output_path: Path) -> str | None:
    """Capture a full-page screenshot with Playwright when available."""
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 1080, "height": 1920})
            await page.goto(url, wait_until="networkidle", timeout=25000)
            await page.screenshot(path=str(output_path), full_page=True)
            await browser.close()
        return str(output_path)
    except Exception as exc:
        logger.warning("Playwright screenshot failed: %s", exc)
        return None


def capture_webpage(url: str, title: str = "trend") -> dict[str, Any]:
    """Fetch metadata/core text and optionally save a screenshot to data/raw."""
    settings.ensure_dirs()
    slug = slugify(title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = settings.raw_dir / f"{timestamp}_{slug}.html"
    json_path = settings.raw_dir / f"{timestamp}_{slug}.json"
    screenshot_path = settings.raw_dir / f"{timestamp}_{slug}.png"

    result: dict[str, Any] = {
        "input_url": url,
        "title": title,
        "description": "",
        "core_text": "",
        "html_path": "",
        "screenshot_path": "",
        "captured_at": timestamp,
    }
    if not url:
        write_json(json_path, result)
        return result

    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Trend2Video-Pro/0.1"})
        response.raise_for_status()
        html_path.write_text(response.text, encoding=response.encoding or "utf-8", errors="ignore")
        soup = BeautifulSoup(response.text, "html.parser")
        page_title = soup.title.get_text(strip=True) if soup.title else title
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag.get("content", "") if description_tag else ""
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
        result.update(
            {
                "title": page_title or title,
                "description": description,
                "core_text": text[:3000],
                "html_path": str(html_path),
            }
        )
    except Exception as exc:
        logger.warning("Web fetch failed: %s", exc)
        result["core_text"] = f"无法抓取网页正文，使用用户输入标题继续生成。错误：{exc}"

    try:
        result["screenshot_path"] = asyncio.run(_capture_with_playwright(url, screenshot_path)) or ""
    except RuntimeError:
        result["screenshot_path"] = ""
    write_json(json_path, result)
    result["raw_json_path"] = str(json_path)
    return result
