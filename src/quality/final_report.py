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
    risks = []
    if topic_score.get("final_opportunity_score", 0) < 70:
        risks.append("选题总分低于70：不建议优先制作，但已按要求生成。")
    if script_score.get("overall_script_score", 0) < 80:
        risks.append("脚本评分仍低于80，建议人工复核事实和表达。")
    if not video_score.get("video_exists"):
        risks.append("视频文件未成功生成，请检查 MoviePy/ffmpeg 环境。")
    if not risks:
        risks.append("未发现阻断发布的明显风险。")

    suggestions = [
        "补充真实案例或数据来源可降低事实风险。",
        "根据账号历史受众调整开头钩子。",
        "发布前人工预览字幕遮挡和封面可读性。",
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
        f"- 选题总分：{topic_score.get('final_opportunity_score')}",
        f"- 脚本总分：{script_score.get('overall_script_score')}",
        f"- 视频质量分：{video_score.get('video_quality_score')}",
        "",
        "## 风险提示",
        *[f"- {risk}" for risk in risks],
        "",
        "## 可优化建议",
        *[f"- {item}" for item in suggestions],
        "",
        "## 生成文件路径",
        *[f"- {key}: {value}" for key, value in file_paths.items()],
    ]
    write_json(json_path, report)
    write_text(md_path, "\n".join(md))
    report.update({"report_json_path": str(json_path), "report_md_path": str(md_path)})
    return report
