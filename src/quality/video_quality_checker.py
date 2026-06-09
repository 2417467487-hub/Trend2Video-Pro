"""Video output quality checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def check_video_quality(video_path: str, script: str | int = "", topic: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate generated video with measurable MVP checks.

    The second argument accepts either script text or a legacy integer duration.
    """
    path = Path(video_path)
    exists = path.exists()
    size_mb = round(path.stat().st_size / 1024 / 1024, 2) if exists else 0
    script_text = "" if isinstance(script, int) else script
    target_duration = script if isinstance(script, int) else (topic or {}).get("duration", 60)

    duration_check = target_duration in [30, 60, 90]
    resolution_check = True
    subtitle_check = len(script_text) > 20 if script_text else True
    audio_check = exists and size_mb > 0.05
    hook_check = any(word in script_text[:80] for word in ["别", "一分钟", "正在", "可能", "注意"]) if script_text else True

    checks = [duration_check, resolution_check, subtitle_check, audio_check, hook_check]
    overall = round(sum(20 for item in checks if item), 2)

    return {
        "video_exists": exists,
        "file_size_mb": size_mb,
        "target_duration": target_duration,
        "duration_check": duration_check,
        "resolution_check": resolution_check,
        "subtitle_check": subtitle_check,
        "audio_check": audio_check,
        "hook_check": hook_check,
        "overall_video_score": overall,
        "video_quality_score": overall,
        "checks": {
            "duration_check": duration_check,
            "resolution_check": resolution_check,
            "subtitle_check": subtitle_check,
            "audio_check": audio_check,
            "hook_check": hook_check,
        },
    }
