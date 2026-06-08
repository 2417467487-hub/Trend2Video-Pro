"""Small file IO utilities used by the pipeline."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def slugify(text: str, max_len: int = 64) -> str:
    """Create a filesystem-safe slug while preserving readable ASCII."""
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.strip(), flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text[:max_len] or "trend").lower()


def write_json(path: Path, data: Any) -> Path:
    """Write JSON with UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_json(path: Path) -> Any:
    """Read JSON with UTF-8 encoding."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> Path:
    """Write text with UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
