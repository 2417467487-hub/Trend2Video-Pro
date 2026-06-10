"""Video producer agent."""

from __future__ import annotations

from typing import Any

from src.pipeline import GenerationRequest, run_generation


def produce_video(topic: dict[str, Any], platform: str, style: str, duration: int) -> dict[str, Any]:
    """Run the existing production pipeline for a topic."""
    return run_generation(
        GenerationRequest(
            title=topic.get("title", "Untitled trend"),
            url=topic.get("url", ""),
            platform=platform,
            style=style,
            duration=duration,
        )
    )
