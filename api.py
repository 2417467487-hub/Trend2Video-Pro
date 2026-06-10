"""FastAPI app for Trend2Video Pro."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.agents.orchestrator import run_trend_to_video
from src.collectors.collector_manager import collect_all_topics
from src.creator.creator_profile import load_creator_profile
from src.database.db import get_topic, list_topics, upsert_topics

app = FastAPI(title="Trend2Video Pro API", version="0.3.0")


class GeneratePayload(BaseModel):
    """Request body for generation endpoints."""

    title: str = "AI Agent Browser Tool Trend"
    url: str = ""
    platform: Literal["Bilibili", "Xiaohongshu", "YouTube Shorts", "TikTok"] = "Bilibili"
    duration: Literal[30, 60, 90] = 60
    style: Literal["Tech News", "Educational", "Viral Talking Head", "Deep Analysis"] = "Tech News"


class GenerateFromTopicPayload(BaseModel):
    """Request body for topic-based generation."""

    platform: Literal["Bilibili", "Xiaohongshu", "YouTube Shorts", "TikTok"] = "Bilibili"
    duration: Literal[30, 60, 90] = 60
    style: Literal["Tech News", "Educational", "Viral Talking Head", "Deep Analysis"] = "Tech News"


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/generate")
def generate(payload: GeneratePayload) -> dict:
    """Generate a video package from a title/link."""
    return run_trend_to_video(
        {"title": payload.title, "url": payload.url, "description": ""},
        creator_profile=load_creator_profile(),
        platform=payload.platform,
        style=payload.style,
        duration=payload.duration,
    )


@app.post("/api/update-topics")
def update_topics() -> dict[str, int]:
    """Collect and store fresh topics."""
    topics = collect_all_topics(limit=20)
    return {"updated": upsert_topics(topics)}


@app.get("/api/topics")
def topics(limit: int = 20) -> list[dict]:
    """List topics by opportunity score."""
    return list_topics(limit=limit)


@app.post("/api/generate-from-topic")
def generate_from_topic(topic_id: int, payload: GenerateFromTopicPayload) -> dict:
    """Generate a video package from a stored topic."""
    topic = get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    return run_trend_to_video(
        topic,
        creator_profile=load_creator_profile(),
        platform=payload.platform,
        style=payload.style,
        duration=payload.duration,
    )
