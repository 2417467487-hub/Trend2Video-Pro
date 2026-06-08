"""Short-video script generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.settings import settings
from src.generation.llm_client import LLMClient
from src.utils.file_utils import write_json, write_text


def generate_script(
    title: str,
    platform: str,
    duration: int,
    style: str,
    topic_score: dict[str, Any],
    page_info: dict[str, Any] | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Generate a publish-oriented spoken script and save Markdown/JSON."""
    page_info = page_info or {}
    prompt = f"""
请为短视频生成自然口播脚本，必须包含3秒强钩子、背景介绍、3个核心信息点、用户收益、结尾引导。
标题：{title}
平台：{platform}
时长：{duration}秒
风格：{style}
选题评分：{topic_score}
网页信息：{page_info.get('description', '')} {page_info.get('core_text', '')[:800]}
要求：不要空泛，不要过度标题党，输出 JSON，包含 title/description/tags/script。
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
