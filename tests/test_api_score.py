from api import ScorePayload, score


def test_score_endpoint_returns_viral_fields():
    payload = score(ScorePayload(title="AI Agent Trend", platform="Bilibili", style="Tech News"))
    assert "viral_probability" in payload
    assert "predicted_views" in payload
    assert "competition_level" in payload
    assert "recommendation" in payload
    assert "explanation" in payload
