"""SRT subtitle generation."""

from __future__ import annotations

import re
from pathlib import Path

from config.settings import settings
from src.utils.file_utils import write_json, write_text


def _chunks(text: str, limit: int = 18) -> list[str]:
    raw = re.split(r"[，。！？,.!?\n]+", text)
    chunks: list[str] = []
    for part in [p.strip() for p in raw if p.strip()]:
        while len(part) > limit:
            chunks.append(part[:limit])
            part = part[limit:]
        if part:
            chunks.append(part)
    return chunks


def _fmt(seconds: float) -> str:
    millis = int((seconds - int(seconds)) * 1000)
    whole = int(seconds)
    h, rem = divmod(whole, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02}:{m:02}:{s:02},{millis:03}"


def generate_srt(text: str, duration: int, output_path: Path | None = None) -> dict[str, object]:
    """Generate SRT and keyword metadata from script text."""
    output_path = output_path or settings.subtitle_dir / "subtitles.srt"
    parts = _chunks(text)
    if not parts:
        raise ValueError("Cannot generate subtitles from empty text.")
    per = max(1.2, duration / len(parts))
    lines = []
    metadata = []
    for idx, subtitle in enumerate(parts, start=1):
        start = (idx - 1) * per
        end = min(duration, idx * per)
        lines.extend([str(idx), f"{_fmt(start)} --> {_fmt(end)}", subtitle, ""])
        keywords = [w for w in ["AI", "工具", "趋势", "机会", "效率"] if w in subtitle]
        metadata.append({"index": idx, "text": subtitle, "keywords": keywords})
    write_text(output_path, "\n".join(lines))
    json_path = output_path.with_suffix(".json")
    write_json(json_path, metadata)
    return {"srt_path": str(output_path), "subtitle_json_path": str(json_path), "items": metadata}
