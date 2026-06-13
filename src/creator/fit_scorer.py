"""Creator-topic fit scoring."""

from __future__ import annotations

from typing import Any


def score_creator_fit(topic: dict[str, Any], creator_profile: dict[str, Any]) -> dict[str, Any]:
    """Score how well a topic fits a creator profile and recommend an angle."""
    text = f"{topic.get('title', '')} {topic.get('description', '')}".lower()
    keywords = [str(item).lower() for item in creator_profile.get("keywords", [])]
    matched_keywords = [keyword for keyword in keywords if keyword and keyword in text]
    platform = topic.get("platform") or topic.get("recommended_platform") or "Bilibili"
    platform_fit = 18 if platform in creator_profile.get("target_platforms", []) else 8
    history = creator_profile.get("past_viral_content") or creator_profile.get("past_successful_content", [])
    history_bonus = min(12, len(history) * 3)
    niche_terms = str(creator_profile.get("niche", "")).lower().replace(",", " ").split()
    niche_bonus = 10 if any(word in text for word in niche_terms if len(word) > 2) else 0
    score = max(0, min(100, 45 + len(matched_keywords) * 8 + platform_fit + history_bonus + niche_bonus))

    if len(matched_keywords) >= 3:
        angle = "Lead with a practical workflow demo and show the before/after creator benefit."
    elif "open-source" in text or "github" in text:
        angle = "Frame it as an open-source tool discovery with a clear use-case teardown."
    elif "ai" in text:
        angle = "Explain the AI trend through one concrete creator workflow, not abstract hype."
    else:
        angle = "Use a problem-solution angle and connect the topic to the audience's next action."

    return {
        "creator_fit_score": round(score, 2),
        "matched_keywords": matched_keywords,
        "platform_fit": platform_fit,
        "recommended_angle": angle,
        "explanation": "Creator fit is based on niche keyword overlap, platform match, and historical content performance.",
    }
