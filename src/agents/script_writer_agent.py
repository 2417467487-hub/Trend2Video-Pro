"""Script writer agent."""

from __future__ import annotations

from typing import Any

from src.generation.script_generator import generate_script


def write_script(topic: dict[str, Any], platform: str, style: str, duration: int) -> dict[str, Any]:
    """Generate a short-video script."""
    return generate_script(topic, platform=platform, style=style, duration=duration)
