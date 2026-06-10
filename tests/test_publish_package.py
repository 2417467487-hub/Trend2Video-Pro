from pathlib import Path

from src.publishing.package_builder import build_publish_package


def test_publish_package_builder(tmp_path):
    video = tmp_path / "video.mp4"
    thumb = tmp_path / "thumb.png"
    subs = tmp_path / "subtitles.srt"
    report = tmp_path / "quality_report.md"
    for path in [video, thumb, subs, report]:
        path.write_bytes(b"demo")
    result = {
        "input": {"title": "AI Agent Browser Tool Trend", "platform": "Bilibili"},
        "script": {"title": "AI Agent Browser Tool Trend", "description": "demo", "tags": ["AI", "Creator"]},
        "files": {"video": str(video), "thumbnail": str(thumb), "subtitles": str(subs), "report_md": str(report)},
    }
    package = build_publish_package(result, output_root=tmp_path / "packages")
    assert Path(package["package_dir"]).exists()
    assert Path(package["metadata"]).exists()
    assert Path(package["title"]).exists()
