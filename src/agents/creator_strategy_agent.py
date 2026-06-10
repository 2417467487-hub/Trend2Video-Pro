"""Creator strategy agent."""

from __future__ import annotations

from typing import Any

from src.creator.fit_scorer import score_creator_fit


def build_creator_strategy(topic: dict[str, Any], creator_profile: dict[str, Any], platform: str, style: str) -> dict[str, Any]:
    """Create a platform-aware creator strategy."""
    fit = score_creator_fit({**topic, "platform": platform}, creator_profile)
    return {
        "creator_fit": fit,
        "recommended_angle": topic.get("recommended_angle", "Explain the practical creator workflow."),
        "tone": creator_profile.get("tone", "clear and practical"),
        "platform": platform,
        "style": style,
    }
