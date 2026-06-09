"""MoviePy-based 9:16 video composer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from config.settings import settings
from src.media.asset_manager import make_gradient_background
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _font(size: int):
    for candidate in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/arial.ttf"]:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap(text: str, width: int = 15) -> str:
    return "\n".join(text[i : i + width] for i in range(0, len(text), width))


def _text_card(text: str, path: Path, title: str = "") -> Path:
    img = Image.new("RGB", (1080, 1920), (10, 22, 46))
    draw = ImageDraw.Draw(img)
    for y in range(1920):
        draw.line([(0, y), (1080, y)], fill=(10, 22 + y // 55, 52 + y // 28))
    draw.rounded_rectangle((70, 150, 1010, 360), radius=30, fill=(0, 185, 220))
    draw.text((105, 205), title[:16] or "Trend2Video Pro", font=_font(66), fill="white")
    draw.text((95, 610), _wrap(text, 13), font=_font(62), fill=(245, 250, 255), spacing=22)
    draw.text((95, 1700), "关注我，继续看懂新趋势", font=_font(42), fill=(180, 235, 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def _prepare_scene_image(scene: dict[str, Any], idx: int, title: str) -> Path:
    scene_dir = settings.output_dir / "scene_cards"
    asset_path = scene.get("asset_path")
    if scene.get("asset_type") == "screenshot" and asset_path and Path(asset_path).exists():
        try:
            img = Image.open(asset_path).convert("RGB")
            img.thumbnail((1000, 1480))
            canvas = Image.open(make_gradient_background(scene_dir / f"scene_{idx}_bg.png")).convert("RGB")
            x = (1080 - img.width) // 2
            canvas.paste(img, (x, 360))
            out = scene_dir / f"scene_{idx}.png"
            canvas.save(out)
            return out
        except Exception as exc:
            logger.warning("Screenshot scene failed, using text card: %s", exc)
    return _text_card(scene.get("subtitle_text", ""), scene_dir / f"scene_{idx}.png", title)


def compose_video(
    storyboard: list[dict[str, Any]],
    audio_path: str,
    subtitle_path: str,
    title: str = "Trend2Video Pro",
    output_path: Path | None = None,
    duration: int = 60,
) -> str:
    """Compose a vertical MP4 with title card, scenes, audio, and simple motion."""
    output_path = output_path or settings.video_dir / "trend_video.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        try:
            from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

            moviepy_v2 = False
        except Exception:
            from moviepy import AudioFileClip, ImageClip, concatenate_videoclips

            moviepy_v2 = True

        def with_duration(clip, seconds: float):
            return clip.with_duration(seconds) if moviepy_v2 else clip.set_duration(seconds)

        def with_fps(clip, fps: int):
            return clip.with_fps(fps) if moviepy_v2 else clip.set_fps(fps)

        def with_audio(clip, audio):
            return clip.with_audio(audio) if moviepy_v2 else clip.set_audio(audio)

        def resized(clip):
            if moviepy_v2:
                return clip.resized(lambda t: 1 + 0.01 * t)
            return clip.resize(lambda t: 1 + 0.01 * t)

        clips = []
        title_card = _text_card(f"{title}\n\n一分钟看懂机会", settings.output_dir / "scene_cards" / "title.png", "热点速递")
        clips.append(resized(with_duration(ImageClip(str(title_card)), 2.5)))
        for idx, scene in enumerate(storyboard, start=1):
            image_path = _prepare_scene_image(scene, idx, title)
            clips.append(resized(with_duration(ImageClip(str(image_path)), float(scene.get("duration", 3)))))
        end_card = _text_card("如果你想持续看懂新工具和新趋势\n关注我，下一条继续拆解", settings.output_dir / "scene_cards" / "end.png", "别错过")
        clips.append(with_duration(ImageClip(str(end_card)), 2.5))

        video = with_fps(concatenate_videoclips(clips, method="compose"), 24)
        if Path(audio_path).exists():
            audio = AudioFileClip(audio_path)
            video = with_duration(with_audio(video, audio), min(video.duration, max(audio.duration, duration)))
        else:
            video = with_duration(video, duration)
        if moviepy_v2:
            video.write_videofile(str(output_path), codec="libx264", audio_codec="aac", fps=24, preset="ultrafast", threads=4, logger=None)
        else:
            video.write_videofile(str(output_path), codec="libx264", audio_codec="aac", fps=24, preset="ultrafast", threads=4, verbose=False, logger=None)
        video.close()
        return str(output_path)
    except Exception as exc:
        logger.warning("MoviePy compose failed: %s", exc)
        placeholder = output_path.with_suffix(".error.txt")
        placeholder.write_text(f"Video generation failed: {exc}\nSubtitles: {subtitle_path}", encoding="utf-8")
        return str(output_path)
