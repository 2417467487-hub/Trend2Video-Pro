"""Quality reviewer agent."""

from __future__ import annotations

from typing import Any


def review_publish_readiness(result: dict[str, Any]) -> dict[str, Any]:
    """Summarize final publish readiness."""
    topic_score = result.get("topic_score", {}).get("final_opportunity_score", 0)
    script_score = result.get("script_score", {}).get("overall_script_score", 0)
    video_score = result.get("video_score", {}).get("overall_video_score", result.get("video_score", {}).get("video_quality_score", 0))
    overall = round((topic_score * 0.3) + (script_score * 0.35) + (video_score * 0.35), 2)
    return {
        "publish_readiness_score": overall,
        "ready": overall >= 75,
        "summary": "Ready for manual preview and publishing." if overall >= 75 else "Needs manual review before publishing.",
    }
