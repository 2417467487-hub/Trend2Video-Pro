"""Feature builder for simple viral prediction."""

from __future__ import annotations

from typing import Any


def build_viral_features(topic: dict[str, Any], creator_fit: dict[str, Any] | None = None, platform: str = "Bilibili") -> dict[str, float]:
    """Build normalized rule-based features for viral prediction."""
    creator_fit = creator_fit or {}
    title = str(topic.get("title", "")).lower()
    hook_strength = 0.45
    if any(token in title for token in ["ai", "agent", "open-source", "launch", "new", "tool", "trend"]):
        hook_strength += 0.25
    if any(token in title for token in ["how", "why", "3", "three", "best", "vs"]):
        hook_strength += 0.15
    return {
        "trend": float(topic.get("trend_score", 50)) / 100,
        "urgency": float(topic.get("urgency_score", 50)) / 100,
        "monetization": float(topic.get("monetization_score", 50)) / 100,
        "creator_fit": float(creator_fit.get("creator_fit_score", topic.get("audience_fit_score", 50))) / 100,
        "competition_inverse": max(0.0, 1 - float(topic.get("competition_score", 50)) / 100),
        "hook_strength": min(1.0, hook_strength),
        "platform_short_video_bonus": 1.0 if platform in ["Xiaohongshu", "YouTube Shorts", "TikTok"] else 0.75,
    }
