"""Text-to-speech generation with edge-tts and fallback silence."""

from __future__ import annotations

import asyncio
import wave
from pathlib import Path

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_VOICES = ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "en-US-AriaNeural"]


def _write_silence_wav(path: Path, duration: int = 8) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b"\x00\x00" * 44100 * duration)
    return path


async def _edge_tts(text: str, path: Path, voice: str, rate: str) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.save(str(path))


def generate_tts(text: str, voice: str = "", rate: str = "+0%", output_path: Path | None = None) -> str:
    """Generate narration audio as MP3; fallback to WAV if edge-tts fails."""
    settings.ensure_dirs()
    voice = voice if voice in SUPPORTED_VOICES else settings.default_tts_voice
    output_path = output_path or settings.audio_dir / "voiceover.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        asyncio.run(_edge_tts(text, output_path, voice, rate))
        return str(output_path)
    except Exception as exc:
        logger.warning("edge-tts failed, writing silent fallback audio: %s", exc)
        fallback = output_path.with_suffix(".wav")
        _write_silence_wav(fallback, duration=max(8, min(90, len(text) // 8)))
        return str(fallback)
