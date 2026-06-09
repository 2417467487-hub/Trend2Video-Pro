from src.generation.storyboard_generator import generate_storyboard


def test_generate_storyboard_maps_voiceover_to_scenes(tmp_path):
    script = "别急着划走，这个趋势正在变化。\n第一，它很新。\n第二，它有用。\n第三，它能行动。\n关注我。"
    scenes = generate_storyboard(script, duration=30, output_path=tmp_path / "storyboard.json")
    assert len(scenes) >= 3
    assert scenes[0]["scene_id"] == 1
    assert scenes[0]["voiceover"]
    assert (tmp_path / "storyboard.json").exists()
