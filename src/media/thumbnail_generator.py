"""Thumbnail image generation."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config.settings import settings
from src.generation.cover_copy_generator import generate_cover_copy


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def generate_thumbnail(title: str, subtitle: str = "", keyword: str = "", output_path: Path | None = None) -> str:
    """Generate a readable tech-style PNG thumbnail."""
    output_path = output_path or settings.thumbnail_dir / "thumbnail.png"
    copy = generate_cover_copy(title)
    headline = title[:18] or copy["headline"]
    subtitle = subtitle or copy["subtitle"]
    keyword = keyword or copy["keyword"]
    img = Image.new("RGB", (1080, 1920), (12, 24, 48))
    draw = ImageDraw.Draw(img)
    for y in range(1920):
        draw.line([(0, y), (1080, y)], fill=(12, 24 + y // 45, 60 + y // 35))
    draw.rounded_rectangle((80, 170, 1000, 420), radius=28, fill=(0, 180, 220))
    draw.text((115, 220), keyword, font=_font(96), fill="white")
    draw.text((90, 620), headline, font=_font(92), fill=(255, 255, 255))
    draw.text((94, 835), subtitle, font=_font(54), fill=(182, 235, 255))
    draw.rectangle((90, 1510, 990, 1520), fill=(0, 220, 255))
    draw.text((90, 1570), "Trend2Video Pro", font=_font(44), fill=(225, 242, 255))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return str(output_path)
