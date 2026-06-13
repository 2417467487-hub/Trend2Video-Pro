"""Run a mock-mode benchmark for Trend2Video Pro."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.creator.creator_profile import load_creator_profile
from src.creator.fit_scorer import score_creator_fit
from src.generation.script_generator import generate_script
from src.prediction.viral_predictor import predict_viral_potential
from src.quality.script_reviewer import review_script
from src.scoring.opportunity_scorer import score_topic


def run_benchmark() -> Path:
    """Score benchmark topics and write a high-signal summary."""
    topics = json.loads((ROOT / "evaluation" / "benchmark_topics.json").read_text(encoding="utf-8"))
    profile = load_creator_profile()
    rows = []
    for topic in topics:
        scored = {**topic, **score_topic(topic, creator_profile=profile)}
        fit = score_creator_fit(scored, profile)
        viral = predict_viral_potential(scored, fit, "Bilibili")
        script = generate_script(scored, platform="Bilibili", style="Tech News", duration=60)
        script_quality = review_script(script["script"], "Bilibili")
        publish_readiness = round(
            (
                scored["final_opportunity_score"]
                + fit["creator_fit_score"]
                + viral["viral_probability"] * 100
                + script_quality["overall_script_score"]
            )
            / 4,
            2,
        )
        rows.append(
            {
                "title": topic["title"],
                "hook_score": script_quality["hook_score"],
                "viral_accuracy": round(viral["viral_probability"], 3),
                "script_quality": script_quality["overall_script_score"],
                "publish_readiness_score": publish_readiness,
            }
        )

    lines = [
        "# Trend2Video Pro Benchmark Summary",
        "",
        "Mock-mode benchmark for the Trend Intelligence + Content Execution pipeline.",
        "",
        "| Topic | Hook Score | Viral Accuracy | Script Quality | Publish Readiness |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['title']} | {row['hook_score']} | {row['viral_accuracy']} | "
            f"{row['script_quality']} | {row['publish_readiness_score']} |"
        )
    output = ROOT / "evaluation" / "benchmark_summary.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


if __name__ == "__main__":
    print(run_benchmark())
