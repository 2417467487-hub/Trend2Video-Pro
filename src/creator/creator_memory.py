"""Simple local creator memory store."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from config.settings import settings
from src.creator.creator_profile import load_creator_profile
from src.utils.file_utils import read_json, write_json


MEMORY_PATH = settings.data_dir / "creator_memory.json"


def load_creator_memory(path: str | Path | None = None) -> dict[str, Any]:
    """Load creator memory with a profile and generation history."""
    memory_path = Path(path) if path else MEMORY_PATH
    if not memory_path.exists():
        memory = {
            "creator_profile": load_creator_profile(),
            "generated_topics": [],
            "updated_at": datetime.now(UTC).isoformat(),
        }
        write_json(memory_path, memory)
    return read_json(memory_path)


def remember_generation(topic: dict[str, Any], result: dict[str, Any], path: str | Path | None = None) -> dict[str, Any]:
    """Append a generation summary to local memory."""
    memory_path = Path(path) if path else MEMORY_PATH
    memory = load_creator_memory(memory_path)
    memory.setdefault("generated_topics", []).append(
        {
            "title": topic.get("title", result.get("input", {}).get("title", "")),
            "platform": result.get("input", {}).get("platform", ""),
            "topic_score": result.get("topic_score", {}).get("final_opportunity_score", 0),
            "video_score": result.get("video_score", {}).get("overall_video_score", 0),
            "created_at": datetime.now(UTC).isoformat(),
        }
    )
    memory["updated_at"] = datetime.now(UTC).isoformat()
    write_json(memory_path, memory)
    return memory
