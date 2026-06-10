from src.prediction.viral_predictor import predict_viral_potential


def test_viral_predictor_outputs_expected_fields():
    result = predict_viral_potential(
        {"trend_score": 80, "urgency_score": 70, "monetization_score": 65, "competition_score": 40},
        {"creator_fit_score": 85},
        "YouTube Shorts",
    )
    assert 0 <= result["viral_probability"] <= 1
    assert result["predicted_view_range"]
    assert result["confidence_level"]
    assert result["explanation"]
