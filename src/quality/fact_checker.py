"""Lightweight factual-risk checker."""

from __future__ import annotations


def check_factual_risk(script: str) -> dict[str, object]:
    """Flag risky absolute claims for the MVP report."""
    risky_terms = [term for term in ["guaranteed", "always", "never", "100%", "only", "best ever"] if term.lower() in script.lower()]
    return {
        "risk_level": "medium" if risky_terms else "low",
        "risky_terms": risky_terms,
        "advice": "Avoid absolute claims and add sources." if risky_terms else "No obvious absolute claims detected.",
    }
