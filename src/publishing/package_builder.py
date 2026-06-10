"""Build local publish packages from generated assets."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import settings
from src.utils.file_utils import slugify, write_json, write_text


def build_publish_package(result: dict[str, Any], output_root: Path | None = None) -> dict[str, Any]:
    """Export a clean publish package directory for creators."""
    output_root = output_root or settings.output_dir / "publish_packages"
    title = result.get("script", {}).get("title") or result.get("input", {}).get("title", "trend-video")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_dir = output_root / f"{timestamp}_{slugify(title, 48)}"
    package_dir.mkdir(parents=True, exist_ok=True)

    files = result.get("files", {})
    copy_map = {
        "video": ("video.mp4", files.get("video")),
        "thumbnail": ("thumbnail.png", files.get("thumbnail")),
        "subtitles": ("subtitles.srt", files.get("subtitles")),
        "quality_report": ("quality_report.md", files.get("report_md")),
    }
    exported: dict[str, str] = {}
    for key, (name, source) in copy_map.items():
        if source and Path(source).exists():
            dest = package_dir / name
            shutil.copy2(source, dest)
            exported[key] = str(dest)

    script = result.get("script", {})
    tags = script.get("tags", [])
    title_path = write_text(package_dir / "title.txt", script.get("title", title))
    description_path = write_text(package_dir / "description.txt", script.get("description", ""))
    hashtags_path = write_text(package_dir / "hashtags.txt", "\n".join([f"#{str(tag).replace(' ', '')}" for tag in tags]))
    metadata = {
        "title": script.get("title", title),
        "description": script.get("description", ""),
        "hashtags": tags,
        "input": result.get("input", {}),
        "topic_score": result.get("topic_score", {}),
        "creator_fit": result.get("creator_fit", {}),
        "viral_prediction": result.get("viral_prediction", {}),
        "script_score": result.get("script_score", {}),
        "video_score": result.get("video_score", {}),
        "source_files": files,
    }
    metadata_path = write_json(package_dir / "metadata.json", metadata)
    exported.update(
        {
            "package_dir": str(package_dir),
            "title": str(title_path),
            "description": str(description_path),
            "hashtags": str(hashtags_path),
            "metadata": str(metadata_path),
        }
    )
    return exported
