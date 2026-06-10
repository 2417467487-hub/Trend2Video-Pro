from src.creator.creator_memory import load_creator_memory, remember_generation
from src.creator.creator_profile import default_creator_profile


def test_creator_memory_roundtrip(tmp_path):
    memory_path = tmp_path / "memory.json"
    memory = load_creator_memory(memory_path)
    memory["creator_profile"] = default_creator_profile()
    updated = remember_generation(
        {"title": "AI Agent Browser Tool Trend"},
        {"input": {"platform": "Bilibili"}, "topic_score": {"final_opportunity_score": 80}, "video_score": {"overall_video_score": 90}},
        memory_path,
    )
    assert updated["generated_topics"]
