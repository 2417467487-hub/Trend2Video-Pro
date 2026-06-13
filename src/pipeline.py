"""End-to-end Trend2Video Pro production pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config.settings import settings
from src.collectors.webpage_screenshot import capture_webpage
from src.database.db import init_db, save_generation_task, save_publish_package_record
from src.generation.script_generator import generate_script
from src.generation.storyboard_generator import generate_storyboard
from src.media.subtitle_generator import generate_srt
from src.media.thumbnail_generator import generate_thumbnail
from src.media.tts_generator import generate_tts
from src.media.video_editor import compose_video
from src.publishing.package_builder import build_publish_package
from src.quality.final_report import generate_final_report
from src.quality.script_reviewer import review_script, rewrite_script_once
from src.quality.video_quality_checker import check_video_quality
from src.scoring.trend_scorer import score_topic
from src.utils.file_utils import write_json
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GenerationRequest:
    """Input fields required by the one-click generator."""

    title: str
    url: str = ""
    platform: str = "Bilibili"
    duration: int = 60
    style: str = "Tech News"
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: str = "+0%"
    topic_id: int | None = None


def run_generation(request: GenerationRequest) -> dict[str, Any]:
    """Run the full video production pipeline and return generated artifacts."""
    settings.ensure_dirs()
    init_db()
    logger.info("Starting generation for %s", request.title)

    page_info = (
        capture_webpage(request.url, request.title)
        if request.url
        else {"title": request.title, "core_text": "", "description": "", "screenshot_path": ""}
    )

    topic_score = score_topic(request.title, request.url, request.platform, request.style, page_info.get("core_text", ""))
    topic_score_path = settings.report_dir / "topic_score.json"
    write_json(topic_score_path, topic_score)

    topic_payload = {
        "title": request.title,
        "url": request.url,
        "description": page_info.get("description", ""),
        **topic_score,
    }
    script_data = generate_script(topic_payload, platform=request.platform, style=request.style, duration=request.duration, page_info=page_info)
    script_score = review_script(script_data["script"], request.platform)
    if script_score["needs_rewrite"]:
        script_data["script"] = rewrite_script_once(script_data["script"], request.platform, request.style)
        script_score = review_script(script_data["script"], request.platform)
        write_json(settings.script_dir / "script.json", script_data)
        (settings.script_dir / "script.md").write_text(f"# {script_data.get('title', request.title)}\n\n{script_data['script']}\n", encoding="utf-8")

    storyboard = generate_storyboard(script_data, request.duration, page_info.get("screenshot_path", ""))
    audio_path = generate_tts(script_data["script"], request.voice, request.rate)
    subtitle_data = generate_srt(script_data["script"], request.duration)
    video_path = compose_video(
        storyboard,
        audio_path,
        subtitle_data["srt_path"],
        script_data.get("title", request.title),
        duration=request.duration,
    )
    thumbnail_path = generate_thumbnail(script_data.get("title", request.title), keyword=request.title[:8])
    video_score = check_video_quality(video_path, script_data["script"], {"duration": request.duration, "title": request.title})

    file_paths = {
        "topic_score": str(topic_score_path),
        "script_md": script_data["script_md_path"],
        "script_json": script_data["script_json_path"],
        "storyboard_json": str(settings.output_dir / "storyboard.json"),
        "audio": audio_path,
        "subtitles": subtitle_data["srt_path"],
        "subtitle_keywords": subtitle_data["subtitle_json_path"],
        "video": video_path,
        "thumbnail": thumbnail_path,
    }
    report = generate_final_report(topic_score, script_score, video_score, file_paths)

    result = {
        "input": request.__dict__,
        "page_info": page_info,
        "topic_score": topic_score,
        "script": script_data,
        "script_score": script_score,
        "storyboard": storyboard,
        "video_score": video_score,
        "report": report,
        "files": file_paths | {"report_md": report["report_md_path"], "report_json": report["report_json_path"]},
    }
    result["publish_package"] = build_publish_package(result)

    try:
        task_id = save_generation_task(
            topic_id=request.topic_id,
            title=request.title,
            platform=request.platform,
            style=request.style,
            duration=request.duration,
            status="completed" if video_score.get("video_exists") else "needs_review",
            output_video_path=video_path,
            output_report_path=report["report_md_path"],
        )
        save_publish_package_record(task_id=task_id, title=request.title, package=result["publish_package"])
    except Exception as exc:
        logger.warning("Database write failed: %s", exc)

    return result
