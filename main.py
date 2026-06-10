"""CLI entrypoint for Trend2Video Pro."""

from __future__ import annotations

import argparse

from src.agents.orchestrator import run_trend_to_video
from src.collectors.collector_manager import collect_all_topics
from src.creator.creator_profile import load_creator_profile
from src.database.db import get_topic, list_topics, upsert_topics

PLATFORMS = ["Bilibili", "Xiaohongshu", "YouTube Shorts", "TikTok"]
STYLES = ["Tech News", "Educational", "Viral Talking Head", "Deep Analysis"]
DURATIONS = [30, 60, 90]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description="Trend2Video Pro: open-source trend-to-video agent framework")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a video from a title/link")
    generate_parser.add_argument("--title", required=True, help="Trend title")
    generate_parser.add_argument("--url", default="", help="Optional source URL")
    generate_parser.add_argument("--platform", default="Bilibili", choices=PLATFORMS)
    generate_parser.add_argument("--style", default="Tech News", choices=STYLES)
    generate_parser.add_argument("--duration", type=int, default=60, choices=DURATIONS)

    subparsers.add_parser("update-topics", help="Collect and score today's topics")

    list_parser = subparsers.add_parser("list-topics", help="List stored topics by opportunity score")
    list_parser.add_argument("--limit", type=int, default=20)

    from_topic_parser = subparsers.add_parser("generate-from-topic", help="Generate a video from a stored topic")
    from_topic_parser.add_argument("--topic-id", type=int, required=True)
    from_topic_parser.add_argument("--platform", default="Bilibili", choices=PLATFORMS)
    from_topic_parser.add_argument("--style", default="Tech News", choices=STYLES)
    from_topic_parser.add_argument("--duration", type=int, default=60, choices=DURATIONS)

    return parser


def cli() -> None:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "generate":
        result = run_trend_to_video(
            {"title": args.title, "url": args.url, "description": ""},
            creator_profile=load_creator_profile(),
            platform=args.platform,
            style=args.style,
            duration=args.duration,
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
        result = run_trend_to_video(
            topic,
            creator_profile=load_creator_profile(),
            platform=args.platform,
            style=args.style,
            duration=args.duration,
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
    print(f"Publish package: {result.get('publish_package', {}).get('package_dir')}")
    print(f"Topic score: {result['topic_score']['final_opportunity_score']}/100")
    print(f"Creator fit: {result.get('creator_fit', {}).get('creator_fit_score', 'n/a')}/100")
    print(f"Viral probability: {result.get('viral_prediction', {}).get('viral_probability', 'n/a')}")


if __name__ == "__main__":
    cli()
