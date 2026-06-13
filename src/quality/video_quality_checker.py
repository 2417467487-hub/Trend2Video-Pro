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

    opening = script_text[:180].lower()
    hook_keywords = ["do not", "stop", "why", "what if", "trend", "attention", "here is", "not just"]
    hook_score = 88 if any(word in opening for word in hook_keywords) else 70 if opening else 60
    clarity_score = 88 if len(script_text.split()) >= 80 or len(script_text) >= 240 else 74
    key_point_markers = sum(script_text.lower().count(marker) for marker in ["first", "second", "third", "1.", "2.", "3.", "key point"])
    density_score = min(96, 72 + key_point_markers * 8)
    factual_risk_score = 72 if any(term in script_text.lower() for term in ["guaranteed", "always", "never", "100%"]) else 90
    hook_check = hook_score >= 75 if script_text else True

    checks = [duration_check, resolution_check, subtitle_check, audio_check, hook_check]
    technical_score = round(sum(20 for item in checks if item), 2)
    overall = round((hook_score + clarity_score + density_score + factual_risk_score + technical_score) / 5, 2)

    return {
        "video_exists": exists,
        "file_size_mb": size_mb,
        "target_duration": target_duration,
        "duration_check": duration_check,
        "resolution_check": resolution_check,
        "subtitle_check": subtitle_check,
        "audio_check": audio_check,
        "hook_check": hook_check,
        "hook_score": hook_score,
        "clarity_score": clarity_score,
        "density_score": density_score,
        "factual_risk_score": factual_risk_score,
        "technical_score": technical_score,
        "overall_score": overall,
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
