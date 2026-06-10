"""Multi-agent orchestrator for trend-to-video execution."""

from __future__ import annotations

from typing import Any

from src.agents.creator_strategy_agent import build_creator_strategy
from src.agents.fact_checker_agent import fact_check_script
from src.agents.quality_reviewer_agent import review_publish_readiness
from src.agents.trend_analyst_agent import analyze_trend
from src.agents.video_producer_agent import produce_video
from src.creator.creator_profile import load_creator_profile
from src.creator.creator_memory import remember_generation
from src.prediction.viral_predictor import predict_viral_potential
from src.publishing.package_builder import build_publish_package


def run_trend_to_video(
    topic: dict[str, Any] | str,
    creator_profile: dict[str, Any] | None = None,
    platform: str = "Bilibili",
    style: str = "Tech News",
    duration: int = 60,
) -> dict[str, Any]:
    """Run the multi-agent trend-to-video workflow.

    The orchestrator delegates analysis, strategy, prediction, production,
    quality review, memory update, and publish-package export.
    """
    creator_profile = creator_profile or load_creator_profile()
    topic_payload = {"title": topic, "url": "", "description": ""} if isinstance(topic, str) else dict(topic)
    analyzed_topic = analyze_trend({**topic_payload, "platform": platform, "style": style}, creator_profile)
    strategy = build_creator_strategy(analyzed_topic, creator_profile, platform, style)
    viral_prediction = predict_viral_potential(analyzed_topic, strategy["creator_fit"], platform)
    result = produce_video(analyzed_topic, platform, style, duration)
    result["analyzed_topic"] = analyzed_topic
    result["creator_strategy"] = strategy
    result["creator_fit"] = strategy["creator_fit"]
    result["viral_prediction"] = viral_prediction
    result["fact_check"] = fact_check_script(result.get("script", {}).get("script", ""))
    result["publish_readiness"] = review_publish_readiness(result)
    result["agent_trace"] = [
        "trend_analyst_agent",
        "creator_strategy_agent",
        "viral_predictor",
        "video_producer_agent",
        "fact_checker_agent",
        "quality_reviewer_agent",
        "package_builder",
    ]
    result["publish_package"] = build_publish_package(result)
    remember_generation(analyzed_topic, result)
    return result
