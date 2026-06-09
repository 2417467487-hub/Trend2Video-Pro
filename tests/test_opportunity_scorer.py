from src.scoring.opportunity_scorer import score_topic


def test_opportunity_scorer_returns_explainable_fields():
    score = score_topic(
        {
            "title": "OpenAI releases a new AI Agent browser tool",
            "url": "https://example.com/agent",
            "description": "A new AI automation workflow for creators.",
        }
    )
    assert 0 <= score["final_opportunity_score"] <= 100
    assert "recommendation_reason" in score
    assert "risk_note" in score
    assert "recommended_platform" in score
    assert "recommended_angle" in score
