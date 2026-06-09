"""CLI and FastAPI entrypoint for Trend2Video Pro."""

from __future__ import annotations

import argparse
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.collectors.collector_manager import collect_all_topics
from src.database.db import get_topic, list_topics, upsert_topics
from src.pipeline import GenerationRequest, run_generation

PLATFORMS = ["B站", "小红书", "YouTube Shorts", "TikTok"]
STYLES = ["科技资讯", "干货讲解", "爆款口播", "深度分析"]
DURATIONS = [30, 60, 90]

app = FastAPI(title="Trend2Video Pro", version="0.2.0")


class GeneratePayload(BaseModel):
    """Request body for the generation API."""

    title: str
    url: str = ""
    platform: Literal["B站", "小红书", "YouTube Shorts", "TikTok"] = "B站"
    duration: Literal[30, 60, 90] = 60
    style: Literal["科技资讯", "干货讲解", "爆款口播", "深度分析"] = "科技资讯"
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: str = "+0%"


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/generate")
def generate(payload: GeneratePayload) -> dict:
    """Run one-click local video generation."""
    return run_generation(GenerationRequest(**payload.model_dump()))


@app.post("/topics/update")
def update_topics_api() -> dict[str, int]:
    """Collect and store fresh topics."""
    topics = collect_all_topics(limit=20)
    return {"updated": upsert_topics(topics)}


@app.get("/topics")
def topics_api(limit: int = 20) -> list[dict]:
    """List stored topics."""
    return list_topics(limit=limit)


@app.post("/topics/{topic_id}/generate")
def generate_from_topic_api(topic_id: int, payload: GeneratePayload) -> dict:
    """Generate a video from a stored topic."""
    topic = get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    request = GenerationRequest(
        topic_id=topic_id,
        title=topic["title"],
        url=topic["url"],
        platform=payload.platform,
        duration=payload.duration,
        style=payload.style,
        voice=payload.voice,
        rate=payload.rate,
    )
    return run_generation(request)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description="Trend2Video Pro: one-click trend-to-video execution engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a video from a title/link")
    generate_parser.add_argument("--title", required=True, help="Trend title")
    generate_parser.add_argument("--url", default="", help="Optional source URL")
    generate_parser.add_argument("--platform", default="B站", choices=PLATFORMS)
    generate_parser.add_argument("--style", default="科技资讯", choices=STYLES)
    generate_parser.add_argument("--duration", type=int, default=60, choices=DURATIONS)
    generate_parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    generate_parser.add_argument("--rate", default="+0%")

    subparsers.add_parser("update-topics", help="Collect and score today's topics")

    list_parser = subparsers.add_parser("list-topics", help="List stored topics by opportunity score")
    list_parser.add_argument("--limit", type=int, default=20)

    from_topic_parser = subparsers.add_parser("generate-from-topic", help="Generate a video from a stored topic")
    from_topic_parser.add_argument("--topic-id", type=int, required=True)
    from_topic_parser.add_argument("--platform", default="B站", choices=PLATFORMS)
    from_topic_parser.add_argument("--style", default="科技资讯", choices=STYLES)
    from_topic_parser.add_argument("--duration", type=int, default=60, choices=DURATIONS)
    from_topic_parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    from_topic_parser.add_argument("--rate", default="+0%")

    return parser


def cli() -> None:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "generate":
        result = run_generation(
            GenerationRequest(
                title=args.title,
                url=args.url,
                platform=args.platform,
                style=args.style,
                duration=args.duration,
                voice=args.voice,
                rate=args.rate,
            )
        )
        _print_generation_result(result)
        return

    if args.command == "update-topics":
        topics = collect_all_topics(limit=20)
        count = upsert_topics(topics)
        print(f"Updated topics: {count}")
        for item in list_topics(limit=5):
            print(f"#{item['id']} [{item['source']}] {item['final_opportunity_score']:.1f} - {item['title']}")
        return

    if args.command == "list-topics":
        rows = list_topics(limit=args.limit)
        if not rows:
            print("No topics found. Run: python main.py update-topics")
            return
        for row in rows:
            print(
                f"#{row['id']} | {row['final_opportunity_score']:.1f} | {row['source']} | "
                f"{row['title']} | {row['url']}"
            )
            print(f"  reason: {row['recommendation_reason']}")
            print(f"  risk: {row['risk_note']}")
        return

    if args.command == "generate-from-topic":
        topic = get_topic(args.topic_id)
        if not topic:
            parser.error(f"Topic id {args.topic_id} not found. Run update-topics and list-topics first.")
        result = run_generation(
            GenerationRequest(
                topic_id=args.topic_id,
                title=topic["title"],
                url=topic["url"],
                platform=args.platform,
                style=args.style,
                duration=args.duration,
                voice=args.voice,
                rate=args.rate,
            )
        )
        _print_generation_result(result)


def _print_generation_result(result: dict) -> None:
    files = result["files"]
    print("Generation complete")
    print(f"Title: {result['script'].get('title', result['input']['title'])}")
    print(f"Video: {files['video']}")
    print(f"Script: {files['script_md']}")
    print(f"Subtitles: {files['subtitles']}")
    print(f"Thumbnail: {files['thumbnail']}")
    print(f"Report: {files['report_md']}")
    print(f"Topic score: {result['topic_score']['final_opportunity_score']}/100")
    print(f"Video quality: {result['video_score'].get('overall_video_score', result['video_score'].get('video_quality_score'))}/100")


if __name__ == "__main__":
    cli()
