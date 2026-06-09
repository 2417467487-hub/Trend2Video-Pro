from pathlib import Path

from src.media.subtitle_generator import generate_srt


def test_generate_srt_limits_chinese_chunks(tmp_path):
    text = "别急着划走，这个AI工具正在改变创作者工作流。第一，它能提效。第二，它能生成素材。"
    result = generate_srt(text, 30, output_path=tmp_path / "subtitles.srt")
    assert Path(result["srt_path"]).exists()
    assert all(len(item["text"]) <= 18 for item in result["items"])
