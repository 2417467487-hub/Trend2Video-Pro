"""Storyboard generation from script text."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from config.settings import settings
from src.utils.file_utils import write_json


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def generate_storyboard(script_data: dict[str, Any], duration: int, screenshot_path: str = "", output_path: Path | None = None) -> list[dict[str, Any]]:
    """Create one visual scene per narration segment."""
    sentences = _split_sentences(script_data.get("script", ""))
    if not sentences:
        raise ValueError("Script is empty; cannot generate storyboard.")
    per_scene = max(2.5, duration / len(sentences))
    scenes: list[dict[str, Any]] = []
    for idx, sentence in enumerate(sentences, start=1):
        asset_type = "screenshot" if screenshot_path and idx in {2, 3} else ("text_card" if idx in {1, len(sentences)} else "stock_placeholder")
        scenes.append(
            {
                "scene_id": idx,
                "voiceover": sentence,
                "visual_instruction": f"竖屏科技风画面，突出：{sentence[:24]}",
                "asset_type": asset_type,
                "asset_path": screenshot_path if asset_type == "screenshot" else "",
                "duration": round(per_scene, 2),
                "subtitle_text": sentence,
            }
        )
    output_path = output_path or settings.output_dir / "storyboard.json"
    write_json(output_path, scenes)
    return scenes
