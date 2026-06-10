"""Short-video script generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.settings import settings
from src.generation.llm_client import LLMClient
from src.utils.file_utils import write_json, write_text


def generate_script(
    topic: dict[str, Any] | str,
    platform: str = "Bilibili",
    style: str = "Tech News",
    duration: int = 60,
    topic_score: dict[str, Any] | None = None,
    page_info: dict[str, Any] | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Generate a publish-oriented spoken script and save Markdown/JSON."""
    if isinstance(topic, dict):
        title = topic.get("title", "Untitled trend")
        page_info = page_info or {"description": topic.get("description", ""), "core_text": ""}
        topic_score = topic_score or topic
    else:
        title = topic
        page_info = page_info or {}
        topic_score = topic_score or {}

    prompt = f"""
Create a natural spoken short-video script with:
1. a strong 3-second hook
2. background context
3. three key information points
4. viewer benefit
5. closing call to action

Title: {title}
Platform: {platform}
Duration: {duration} seconds
Style: {style}
Topic score: {topic_score}
Source context: {page_info.get('description', '')} {page_info.get('core_text', '')[:800]}

Return JSON with title, description, tags, and script. Avoid vague hype and empty claims.
"""
    data = LLMClient().generate_json(prompt, task="script")
    script = data.get("script", "")
    output_dir = output_dir or settings.script_dir
    md_path = output_dir / "script.md"
    json_path = output_dir / "script.json"
    markdown = f"# {data.get('title', title)}\n\n{script}\n\n## Tags\n{', '.join(data.get('tags', []))}\n"
    write_text(md_path, markdown)
    data.update({"script_md_path": str(md_path), "script_json_path": str(json_path)})
    write_json(json_path, data)
    return data
