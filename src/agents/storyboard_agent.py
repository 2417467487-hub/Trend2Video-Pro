"""Storyboard agent."""

from __future__ import annotations

from typing import Any

from src.generation.storyboard_generator import generate_storyboard


def build_storyboard(script_data: dict[str, Any], duration: int) -> list[dict[str, Any]]:
    """Create a storyboard from script data."""
    return generate_storyboard(script_data, duration=duration)
