"""Explainable trend and opportunity scoring."""

from __future__ import annotations

import re
from typing import Any


HOT_KEYWORDS = [
    "ai",
    "agent",
    "openai",
    "deepseek",
    "qwen",
    "github",
    "product hunt",
    "browser",
    "automation",
    "trending",
    "launch",
    "release",
    "viral",
    "open source",
    "workflow",
]

MONETIZATION_KEYWORDS = [
    "tool",
    "product",
    "saas",
    "creator",
    "automation",
    "workflow",
    "growth",
    "course",
    "paid",
    "business",
]

COMPETITION_KEYWORDS = ["openai", "chatgpt", "ai", "agent", "viral", "trending"]
URGENCY_KEYWORDS = ["today", "now", "new", "latest", "launch", "release", "2026", "trending"]


def _clamp(value: float) -> float:
    """Clamp a score to 0-100."""
    return max(0.0, min(100.0, round(value, 2)))


def _count_hits(text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword.lower() in text)


def score_topic(
    title: str,
    url: str = "",
    platform: str = "Bilibili",
    style: str = "Tech News",
    page_text: str = "",
    creator_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Score a topic with transparent heuristic rules.

    Formula:
    final_score = 0.30 * trend + 0.20 * audience_fit + 0.20 * monetization
                + 0.20 * urgency - 0.10 * competition
    """
    creator_profile = creator_profile or {}
    text = f"{title} {url} {page_text}".lower()
    hot_hits = _count_hits(text, HOT_KEYWORDS)
    monetization_hits = _count_hits(text, MONETIZATION_KEYWORDS)
    competition_hits = _count_hits(text, COMPETITION_KEYWORDS)
    urgency_hits = _count_hits(text, URGENCY_KEYWORDS)

    has_url = bool(url)
    has_specific_context = len(page_text.strip()) > 80 or bool(re.search(r"\d+", title))
    platform_bonus = 12 if platform in ["Bilibili", "YouTube Shorts"] else 9
    style_bonus = 10 if style in ["Tech News", "Educational"] else 6
    niche_keywords = creator_profile.get("keywords", [])
    profile_hits = sum(1 for keyword in niche_keywords if str(keyword).lower() in text)

    trend_score = _clamp(48 + hot_hits * 8 + urgency_hits * 5 + (6 if has_specific_context else 0))
    competition_score = _clamp(30 + competition_hits * 9 + (10 if hot_hits >= 3 else 0))
    monetization_score = _clamp(45 + monetization_hits * 8 + (8 if any(k in text for k in ["tool", "saas", "workflow"]) else 0))
    audience_fit_score = _clamp(55 + platform_bonus + style_bonus + profile_hits * 6)
    urgency_score = _clamp(44 + urgency_hits * 10 + (14 if has_url else 4) + (4 if "github" in text else 0))

    final_score = _clamp(
        0.30 * trend_score
        + 0.20 * audience_fit_score
        + 0.20 * monetization_score
        + 0.20 * urgency_score
        - 0.10 * competition_score
    )

    recommended_platform = platform
    if "github" in text or "open source" in text:
        recommended_platform = "Bilibili"
    elif "product" in text or "tool" in text:
        recommended_platform = "YouTube Shorts"

    recommended_angle = "Explain why the trend matters and what creators can do with it in one minute."
    if final_score >= 78:
        recommendation_reason = "Strong trend signal, timeliness, and creator-content conversion potential."
        risk_note = "Add sources and avoid overstating product capabilities."
    elif final_score >= 70:
        recommendation_reason = "Worth producing if you add a clear case, demo, or opinion."
        risk_note = "Competition may be high; make the hook specific."
    else:
        recommendation_reason = "Not recommended as a priority unless it strongly matches your creator niche."
        risk_note = "Trend strength or monetization signal is weak; collect more context."

    return {
        "trend_score": trend_score,
        "competition_score": competition_score,
        "monetization_score": monetization_score,
        "audience_fit_score": audience_fit_score,
        "urgency_score": urgency_score,
        "final_opportunity_score": final_score,
        "recommendation": "recommended" if final_score >= 70 else "not_priority",
        "recommendation_reason": recommendation_reason,
        "risk_note": risk_note,
        "recommended_platform": recommended_platform,
        "recommended_angle": recommended_angle,
        "explanation": "Rule-based score using trend keywords, platform fit, monetization, urgency, and competition.",
    }
