from src.scoring.trend_scorer import score_topic


def test_score_topic_has_expected_formula_fields():
    score = score_topic("OpenAI 新 AI 工具发布", "https://example.com", "B站", "科技资讯")
    assert set(
        [
            "trend_score",
            "competition_score",
            "monetization_score",
            "audience_fit_score",
            "urgency_score",
            "final_opportunity_score",
        ]
    ).issubset(score)
    assert 0 <= score["final_opportunity_score"] <= 100
