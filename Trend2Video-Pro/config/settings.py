"""Application settings for Trend2Video Pro."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


class Settings:
    """Environment-backed settings with safe local defaults."""

    root_dir: Path = ROOT_DIR
    data_dir: Path = ROOT_DIR / "data"
    raw_dir: Path = data_dir / "raw"
    asset_dir: Path = data_dir / "assets"
    template_dir: Path = data_dir / "templates"
    output_dir: Path = ROOT_DIR / os.getenv("OUTPUT_DIR", "outputs")
    audio_dir: Path = output_dir / "audio"
    video_dir: Path = output_dir / "videos"
    script_dir: Path = output_dir / "scripts"
    subtitle_dir: Path = output_dir / "subtitles"
    thumbnail_dir: Path = output_dir / "thumbnails"
    report_dir: Path = output_dir / "reports"
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{data_dir / 'trend2video.db'}")
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock").lower()
    llm_model: str = os.getenv("LLM_MODEL", "mock-trend2video")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    qwen_api_key: str = os.getenv("QWEN_API_KEY", "")
    default_tts_voice: str = os.getenv("DEFAULT_TTS_VOICE", "zh-CN-XiaoxiaoNeural")

    def ensure_dirs(self) -> None:
        """Create runtime directories if they do not exist."""
        for path in [
            self.raw_dir,
            self.asset_dir,
            self.template_dir,
            self.audio_dir,
            self.video_dir,
            self.script_dir,
            self.subtitle_dir,
            self.thumbnail_dir,
            self.report_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
