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
from src.prediction.viral_predictor import predict_viral_potential
from src.scoring.opportunity_scorer import score_topic


def run_benchmark() -> Path:
    """Score benchmark topics and write a summary."""
    topics = json.loads((ROOT / "evaluation" / "benchmark_topics.json").read_text(encoding="utf-8"))
    profile = load_creator_profile()
    rows = []
    for topic in topics:
        scored = {**topic, **score_topic(topic, creator_profile=profile)}
        fit = score_creator_fit(scored, profile)
        viral = predict_viral_potential(scored, fit, "Bilibili")
        rows.append((topic["title"], scored["final_opportunity_score"], fit["creator_fit_score"], viral["viral_probability"]))

    lines = [
        "# Trend2Video Pro Benchmark Summary",
        "",
        "| Topic | Opportunity | Creator Fit | Viral Probability |",
        "| --- | ---: | ---: | ---: |",
    ]
    for title, opportunity, fit, viral in rows:
        lines.append(f"| {title} | {opportunity} | {fit} | {viral} |")
    output = ROOT / "evaluation" / "benchmark_summary.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


if __name__ == "__main__":
    print(run_benchmark())
