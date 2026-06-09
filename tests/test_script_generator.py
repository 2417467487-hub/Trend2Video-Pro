from src.generation.script_generator import generate_script
from src.quality.script_reviewer import review_script


def test_generate_script_uses_mock_without_api_key(tmp_path):
    data = generate_script(
        {"title": "OpenAI 新趋势", "description": "AI workflow trend"},
        platform="B站",
        style="科技资讯",
        duration=60,
        output_dir=tmp_path,
    )
    assert "script" in data
    assert (tmp_path / "script.md").exists()
    assert review_script(data["script"])["overall_script_score"] > 0
