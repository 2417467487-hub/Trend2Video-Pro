"""Final generation report writer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.settings import settings
from src.utils.file_utils import write_json, write_text


def generate_final_report(
    topic_score: dict[str, Any],
    script_score: dict[str, Any],
    video_score: dict[str, Any],
    file_paths: dict[str, str],
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Write markdown and JSON quality-control reports."""
    output_dir = output_dir or settings.report_dir
    risks: list[str] = []

    if topic_score.get("final_opportunity_score", 0) < 70:
        risks.append("Topic score is below 70: not recommended for priority production, but assets were generated.")
    if script_score.get("overall_script_score", 0) < 80:
        risks.append("Script score is below 80 after review; manual fact and expression review is recommended.")
    if not video_score.get("video_exists"):
        risks.append("Video file was not created successfully. Check MoviePy/ffmpeg runtime.")
    if not risks:
        risks.append("No blocking publishing risk detected in the MVP checks.")

    suggestions = [
        "Add source links or concrete examples to reduce factual risk.",
        "Tune the opening hook for the creator account and target platform.",
        "Preview subtitle placement and thumbnail readability before publishing.",
    ]

    report = {
        "topic_score": topic_score,
        "script_score": script_score,
        "video_score": video_score,
        "risks": risks,
        "suggestions": suggestions,
        "generated_files": file_paths,
    }

    json_path = output_dir / "quality_report.json"
    md_path = output_dir / "quality_report.md"
    md = [
        "# Trend2Video Pro Quality Report",
        "",
        f"Topic Opportunity Score: {topic_score.get('final_opportunity_score')}/100",
        f"Script Quality Score: {script_score.get('overall_script_score')}/100",
        f"Video Quality Score: {video_score.get('overall_video_score', video_score.get('video_quality_score'))}/100",
        "",
        "## Topic Scores",
        f"- Trend: {topic_score.get('trend_score')}",
        f"- Competition: {topic_score.get('competition_score')}",
        f"- Monetization: {topic_score.get('monetization_score')}",
        f"- Audience Fit: {topic_score.get('audience_fit_score')}",
        f"- Urgency: {topic_score.get('urgency_score')}",
        "",
        "## Risks",
        *[f"- {risk}" for risk in risks],
        "",
        "## Optimization Suggestions",
        *[f"- {item}" for item in suggestions],
        "",
        "## Generated Files",
        *[f"- {key}: {value}" for key, value in file_paths.items()],
    ]
    write_json(json_path, report)
    write_text(md_path, "\n".join(md))
    report.update({"report_json_path": str(json_path), "report_md_path": str(md_path)})
    return report
