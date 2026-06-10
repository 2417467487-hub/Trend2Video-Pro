"""Creator profile loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.settings import settings
from src.utils.file_utils import read_json, write_json


DEFAULT_PROFILE_PATH = settings.root_dir / "creator_profiles" / "default_creator.json"


def default_creator_profile() -> dict[str, Any]:
    """Return a sensible default profile for demo mode."""
    return {
        "creator_name": "Trend2Video Demo Creator",
        "niche": "AI tools, creator workflows, and practical tech explainers",
        "keywords": ["ai", "agent", "automation", "workflow", "creator", "tool", "browser"],
        "target_platforms": ["Bilibili", "Xiaohongshu", "YouTube Shorts", "TikTok"],
        "tone": "clear, practical, fast-paced, non-hype",
        "audience": "solo creators, students, AI tool users, tech bloggers",
        "past_successful_content": [
            {
                "title": "How AI browser agents change creator research",
                "platform": "Bilibili",
                "angle": "show the workflow, not just the product",
                "views": 28000,
            },
            {
                "title": "Three AI tools that save creators one hour per day",
                "platform": "YouTube Shorts",
                "angle": "practical use cases and clear CTA",
                "views": 42000,
            },
        ],
    }


def load_creator_profile(path: str | Path | None = None) -> dict[str, Any]:
    """Load a creator profile; create the default profile if missing."""
    profile_path = Path(path) if path else DEFAULT_PROFILE_PATH
    if not profile_path.exists():
        write_json(profile_path, default_creator_profile())
    return read_json(profile_path)


def save_creator_profile(profile: dict[str, Any], path: str | Path | None = None) -> Path:
    """Save a creator profile to disk."""
    profile_path = Path(path) if path else DEFAULT_PROFILE_PATH
    return write_json(profile_path, profile)
