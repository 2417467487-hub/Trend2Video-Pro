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
    "爆火",
    "上线",
    "发布",
    "趋势",
    "新工具",
    "开源",
]

MONETIZATION_KEYWORDS = [
    "工具",
    "产品",
    "课程",
    "效率",
    "商业",
    "增长",
    "创作者",
    "付费",
    "自动化",
    "workflow",
    "saas",
]

COMPETITION_KEYWORDS = ["openai", "chatgpt", "ai", "agent", "爆火", "全网", "viral"]
URGENCY_KEYWORDS = ["today", "now", "刚刚", "最新", "发布", "上线", "爆火", "2026", "trending"]


def _clamp(value: float) -> float:
    """Clamp a score to 0-100."""
    return max(0.0, min(100.0, round(value, 2)))


def _count_hits(text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword.lower() in text)


def score_topic(
    title: str,
    url: str = "",
    platform: str = "B站",
    style: str = "科技资讯",
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
    platform_bonus = 12 if platform in ["B站", "YouTube Shorts"] else 9
    style_bonus = 10 if style in ["科技资讯", "干货讲解"] else 6
    niche_keywords = creator_profile.get("keywords", [])
    profile_hits = sum(1 for keyword in niche_keywords if str(keyword).lower() in text)

    trend_score = _clamp(48 + hot_hits * 8 + urgency_hits * 5 + (6 if has_specific_context else 0))
    competition_score = _clamp(30 + competition_hits * 9 + (10 if hot_hits >= 3 else 0))
    monetization_score = _clamp(45 + monetization_hits * 8 + (8 if any(k in text for k in ["工具", "saas", "workflow"]) else 0))
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
    if "github" in text or "开源" in text:
        recommended_platform = "B站"
    elif "product" in text or "tool" in text:
        recommended_platform = "YouTube Shorts"

    recommended_angle = "用一分钟解释它为什么值得关注，以及普通创作者能怎么用。"
    if final_score >= 78:
        recommendation_reason = "热点信号、时效性和内容转化空间都较强，建议优先制作。"
        risk_note = "注意补充来源，避免夸大产品能力。"
    elif final_score >= 70:
        recommendation_reason = "选题具备可制作价值，但需要更明确的案例或观点。"
        risk_note = "竞争可能偏高，开头需要更具体。"
    else:
        recommendation_reason = "不建议优先制作，除非该话题与你的账号定位高度相关。"
        risk_note = "热点强度或变现潜力不足，建议补充更多上下文。"

    return {
        "trend_score": trend_score,
        "competition_score": competition_score,
        "monetization_score": monetization_score,
        "audience_fit_score": audience_fit_score,
        "urgency_score": urgency_score,
        "final_opportunity_score": final_score,
        "recommendation": "建议优先制作" if final_score >= 70 else "不建议优先制作",
        "recommendation_reason": recommendation_reason,
        "risk_note": risk_note,
        "recommended_platform": recommended_platform,
        "recommended_angle": recommended_angle,
        "explanation": "基于关键词热度、平台适配、商业潜力、时效性和竞争度的可解释公式评分。",
    }
