from pathlib import Path

from src.generation.storyboard_generator import generate_storyboard
from src.media.subtitle_generator import generate_srt
from src.media.thumbnail_generator import generate_thumbnail


def test_storyboard_subtitle_thumbnail(tmp_path):
    script = "别急着划走，这个趋势正在变化。\n第一，它很新。\n第二，它有用。\n第三，它能行动。\n关注我。"
    scenes = generate_storyboard({"script": script}, 30, output_path=tmp_path / "storyboard.json")
    subtitles = generate_srt(script, 30, output_path=tmp_path / "subtitles.srt")
    thumbnail = generate_thumbnail("OpenAI 新趋势", output_path=tmp_path / "thumb.png")
    assert len(scenes) >= 3
    assert Path(subtitles["srt_path"]).exists()
    assert Path(thumbnail).exists()
