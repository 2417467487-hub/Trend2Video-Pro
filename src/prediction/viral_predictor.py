"""Rule-based viral prediction MVP."""

from __future__ import annotations

from typing import Any

from src.prediction.feature_builder import build_viral_features


def predict_viral_potential(topic: dict[str, Any], creator_fit: dict[str, Any] | None = None, platform: str = "Bilibili") -> dict[str, Any]:
    """Predict viral potential with a transparent baseline."""
    features = build_viral_features(topic, creator_fit, platform)
    probability = (
        0.28 * features["trend"]
        + 0.20 * features["urgency"]
        + 0.18 * features["creator_fit"]
        + 0.14 * features["monetization"]
        + 0.12 * features["competition_inverse"]
        + 0.08 * features["platform_short_video_bonus"]
    )
    probability = max(0.05, min(0.95, round(probability, 3)))
    if probability >= 0.72:
        view_range = "50k-250k"
        confidence = "medium-high"
    elif probability >= 0.55:
        view_range = "10k-50k"
        confidence = "medium"
    else:
        view_range = "1k-10k"
        confidence = "low-medium"
    return {
        "viral_probability": probability,
        "predicted_view_range": view_range,
        "confidence_level": confidence,
        "features": features,
        "explanation": "Rule-based MVP using trend, urgency, creator fit, monetization, competition, and platform fit.",
    }
