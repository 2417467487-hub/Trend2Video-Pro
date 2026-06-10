"""Fact checker agent."""

from __future__ import annotations

from src.quality.fact_checker import check_factual_risk


def fact_check_script(script: str) -> dict[str, object]:
    """Run lightweight factual-risk checks."""
    return check_factual_risk(script)
