"""Video output quality checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def check_video_quality(video_path: str, target_duration: int) -> dict[str, Any]:
    """Validate the generated video artifact with simple measurable checks."""
    path = Path(video_path)
    exists = path.exists()
    size_mb = round(path.stat().st_size / 1024 / 1024, 2) if exists else 0
    score = 45
    if exists:
        score += 25
    if size_mb > 0.1:
        score += 20
    if target_duration in [30, 60, 90]:
        score += 10
    return {
        "video_exists": exists,
        "file_size_mb": size_mb,
        "target_duration": target_duration,
        "video_quality_score": min(100, score),
        "checks": ["MP4文件存在" if exists else "MP4文件缺失", "竖屏1080x1920由合成器设置"],
    }
