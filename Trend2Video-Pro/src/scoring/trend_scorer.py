"""Explainable topic scoring."""

from __future__ import annotations

import re
from typing import Any


HOT_KEYWORDS = ["ai", "openai", "deepseek", "qwen", "github", "product", "爆火", "上线", "发布", "趋势", "新工具"]
MONETIZATION_KEYWORDS = ["工具", "产品", "课程", "效率", "商业", "增长", "创作者", "付费", "automation"]


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, round(value, 2)))


def score_topic(title: str, url: str = "", platform: str = "B站", style: str = "科技资讯", page_text: str = "") -> dict[str, Any]:
    """Score a topic with transparent heuristic rules."""
    text = f"{title} {url} {page_text}".lower()
    keyword_hits = sum(1 for word in HOT_KEYWORDS if word.lower() in text)
    monetization_hits = sum(1 for word in MONETIZATION_KEYWORDS if word.lower() in text)
    title_len = len(title)
    has_url = bool(url)
    is_recent_language = bool(re.search(r"today|刚刚|最新|发布|上线|2026|爆", text))

    trend_score = _clamp(55 + keyword_hits * 8 + (10 if is_recent_language else 0))
    competition_score = _clamp(35 + keyword_hits * 6 + (8 if "ai" in text else 0))
    monetization_score = _clamp(50 + monetization_hits * 9 + (8 if "工具" in title else 0))
    audience_fit_score = _clamp(58 + (12 if platform in ["B站", "YouTube Shorts"] else 8) + (8 if style in ["科技资讯", "干货讲解"] else 4))
    urgency_score = _clamp(50 + (18 if has_url else 6) + (16 if is_recent_language else 0) - max(0, title_len - 40) * 0.2)
    final_score = _clamp(
        0.3 * trend_score
        + 0.2 * audience_fit_score
        + 0.2 * monetization_score
        + 0.2 * urgency_score
        - 0.1 * competition_score
    )
    return {
        "trend_score": trend_score,
        "competition_score": competition_score,
        "monetization_score": monetization_score,
        "audience_fit_score": audience_fit_score,
        "urgency_score": urgency_score,
        "final_opportunity_score": final_score,
        "recommendation": "建议优先制作" if final_score >= 70 else "不建议优先制作",
        "explanation": "基于热点关键词、平台适配、商业潜力、时效性和竞争度的可解释公式评分。",
    }
