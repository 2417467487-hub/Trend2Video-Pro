"""CLI and FastAPI entrypoint for Trend2Video Pro."""

from __future__ import annotations

import argparse
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from src.pipeline import GenerationRequest, run_generation

app = FastAPI(title="Trend2Video Pro", version="0.1.0")


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


def cli() -> None:
    """Run the generator from the command line."""
    parser = argparse.ArgumentParser(description="Trend2Video Pro one-click generator")
    parser.add_argument("--title", required=True, help="热点标题")
    parser.add_argument("--url", default="", help="热点链接")
    parser.add_argument("--platform", default="B站", choices=["B站", "小红书", "YouTube Shorts", "TikTok"])
    parser.add_argument("--duration", type=int, default=60, choices=[30, 60, 90])
    parser.add_argument("--style", default="科技资讯", choices=["科技资讯", "干货讲解", "爆款口播", "深度分析"])
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    parser.add_argument("--rate", default="+0%")
    args = parser.parse_args()
    result = run_generation(GenerationRequest(**vars(args)))
    print("生成完成：")
    print(f"视频：{result['files']['video']}")
    print(f"报告：{result['files']['report_md']}")


if __name__ == "__main__":
    cli()
