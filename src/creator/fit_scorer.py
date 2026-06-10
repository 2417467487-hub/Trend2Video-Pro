"""Creator-topic fit scoring."""

from __future__ import annotations

from typing import Any


def score_creator_fit(topic: dict[str, Any], creator_profile: dict[str, Any]) -> dict[str, Any]:
    """Score how well a topic fits a creator profile."""
    text = f"{topic.get('title', '')} {topic.get('description', '')}".lower()
    keywords = [str(item).lower() for item in creator_profile.get("keywords", [])]
    keyword_hits = sum(1 for keyword in keywords if keyword and keyword in text)
    platform = topic.get("platform") or topic.get("recommended_platform") or "Bilibili"
    platform_fit = 18 if platform in creator_profile.get("target_platforms", []) else 8
    history_bonus = min(12, len(creator_profile.get("past_successful_content", [])) * 3)
    niche_bonus = 10 if any(word in text for word in str(creator_profile.get("niche", "")).lower().split()) else 0
    score = max(0, min(100, 45 + keyword_hits * 8 + platform_fit + history_bonus + niche_bonus))
    return {
        "creator_fit_score": round(score, 2),
        "matched_keywords": [keyword for keyword in keywords if keyword and keyword in text],
        "platform_fit": platform_fit,
        "explanation": "Creator fit is based on niche keyword overlap, platform match, and successful content history.",
    }
