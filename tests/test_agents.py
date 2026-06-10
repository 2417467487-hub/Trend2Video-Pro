from src.agents.trend_analyst_agent import analyze_trend
from src.agents.creator_strategy_agent import build_creator_strategy
from src.creator.creator_profile import default_creator_profile


def test_agents_analyze_and_strategy():
    profile = default_creator_profile()
    topic = analyze_trend({"title": "AI Agent Browser Tool Trend", "description": "creator workflow automation"}, profile)
    strategy = build_creator_strategy(topic, profile, "Bilibili", "Tech News")
    assert topic["final_opportunity_score"] >= 0
    assert strategy["creator_fit"]["creator_fit_score"] >= 0
