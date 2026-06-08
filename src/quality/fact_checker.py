"""Lightweight factual-risk checker."""

from __future__ import annotations


def check_factual_risk(script: str) -> dict[str, object]:
    """Flag risky absolute claims for the MVP report."""
    risky_terms = [term for term in ["绝对", "唯一", "保证", "百分百"] if term in script]
    return {
        "risk_level": "medium" if risky_terms else "low",
        "risky_terms": risky_terms,
        "advice": "避免绝对化承诺，必要时补充来源。" if risky_terms else "未发现明显绝对化表述。",
    }
