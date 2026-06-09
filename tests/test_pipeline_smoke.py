from pathlib import Path

from src.pipeline import GenerationRequest, run_generation


def test_pipeline_smoke_generates_report_script_and_subtitle(monkeypatch, tmp_path):
    video_path = tmp_path / "trend_video.mp4"

    def fake_tts(*args, **kwargs):
        audio = tmp_path / "voiceover.wav"
        audio.write_bytes(b"placeholder")
        return str(audio)

    def fake_video(*args, **kwargs):
        video_path.write_bytes(b"mp4 placeholder")
        return str(video_path)

    monkeypatch.setattr("src.pipeline.generate_tts", fake_tts)
    monkeypatch.setattr("src.pipeline.compose_video", fake_video)

    result = run_generation(
        GenerationRequest(
            title="AI Agent 浏览器插件正在变成新趋势",
            platform="B站",
            style="科技资讯",
            duration=30,
        )
    )
    assert Path(result["files"]["script_md"]).exists()
    assert Path(result["files"]["subtitles"]).exists()
    assert Path(result["files"]["report_md"]).exists()
    assert result["video_score"]["video_exists"] is True
