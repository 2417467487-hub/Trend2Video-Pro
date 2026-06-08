"""Asset helpers for generated media."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def make_gradient_background(path: Path, size: tuple[int, int] = (1080, 1920)) -> Path:
    """Create a simple tech-style gradient background."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        ratio = y / size[1]
        color = (int(12 + ratio * 18), int(28 + ratio * 45), int(58 + ratio * 90))
        draw.line([(0, y), (size[0], y)], fill=color)
    for x in range(0, size[0], 120):
        draw.line([(x, 0), (x + 420, size[1])], fill=(40, 110, 180), width=2)
    img.save(path)
    return path
