"""Script quality review and rewrite trigger."""

from __future__ import annotations

import re
from typing import Any

from src.generation.llm_client import LLMClient


def review_script(script: str, platform: str = "B站") -> dict[str, Any]:
    """Score script quality across hook, clarity, density, risk, and fit."""
    clean = script.strip()
    sentences = [s for s in re.split(r"[。！？!?\n]+", clean) if s.strip()]
    hook = sentences[0] if sentences else ""
    has_three_points = len(re.findall(r"第一|第二|第三|1|2|3", clean)) >= 2
    has_benefit = any(word in clean for word in ["收益", "好处", "你可以", "不用", "知道"])
    has_cta = any(word in clean for word in ["关注", "评论", "收藏", "下一条"])
    vague_terms = sum(clean.count(word) for word in ["非常", "很多", "很重要", "巨大", "颠覆", "绝对"])

    hook_score = min(100, 62 + (24 if len(hook) <= 55 and any(w in hook for w in ["别", "一分钟", "正在", "可能", "先"]) else 8))
    clarity_score = min(100, 58 + min(len(sentences), 9) * 4 + (6 if has_three_points else 0))
    information_density_score = min(100, 56 + (18 if has_three_points else 0) + (8 if has_benefit else 0) + min(len(clean) // 90, 14))
    factual_risk_score = max(35, 90 - vague_terms * 7)
    platform_fit_score = 86 if platform in ["B站", "小红书", "YouTube Shorts", "TikTok"] and has_cta else 74
    overall = round((hook_score + clarity_score + information_density_score + factual_risk_score + platform_fit_score) / 5, 2)
    return {
        "hook_score": hook_score,
        "clarity_score": clarity_score,
        "information_density_score": information_density_score,
        "factual_risk_score": factual_risk_score,
        "platform_fit_score": platform_fit_score,
        "overall_script_score": overall,
        "needs_rewrite": overall < 80,
    }


def rewrite_script_once(script: str, platform: str, style: str) -> str:
    """Ask the LLM to rewrite the script once when quality is low."""
    prompt = f"请重写短视频口播脚本，提高钩子、信息密度和平台适配。平台：{platform}，风格：{style}。原稿：{script}"
    return LLMClient().generate_json(prompt, task="rewrite").get("script", script)
