"""Script quality review and rewrite trigger."""

from __future__ import annotations

import re
from typing import Any

from src.generation.llm_client import LLMClient


def review_script(script: str, platform: str = "Bilibili") -> dict[str, Any]:
    """Score script quality across hook, clarity, density, risk, and fit."""
    clean = script.strip()
    sentences = [s for s in re.split(r"[.!?\n]+", clean) if s.strip()]
    hook = sentences[0] if sentences else ""
    has_three_points = len(re.findall(r"first|second|third|1|2|3", clean.lower())) >= 2
    has_benefit = any(word in clean.lower() for word in ["benefit", "viewer", "you can", "without", "decide"])
    has_cta = any(word in clean.lower() for word in ["follow", "comment", "save", "next"])
    vague_terms = sum(clean.lower().count(word) for word in ["amazing", "insane", "guaranteed", "best ever", "revolutionary"])

    hook_score = min(100, 62 + (24 if len(hook) <= 90 and any(w in hook.lower() for w in ["do not", "stop", "not just", "trend"]) else 8))
    clarity_score = min(100, 58 + min(len(sentences), 9) * 4 + (6 if has_three_points else 0))
    information_density_score = min(100, 56 + (18 if has_three_points else 0) + (8 if has_benefit else 0) + min(len(clean) // 120, 14))
    factual_risk_score = max(35, 90 - vague_terms * 7)
    platform_fit_score = 86 if platform in ["Bilibili", "Xiaohongshu", "YouTube Shorts", "TikTok"] and has_cta else 74
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
    prompt = f"Rewrite this short-video script for a stronger hook, higher information density, and better platform fit. Platform: {platform}. Style: {style}. Original: {script}"
    return LLMClient().generate_json(prompt, task="rewrite").get("script", script)
