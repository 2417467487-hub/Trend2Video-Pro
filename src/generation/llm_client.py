"""Unified LLM client with mock fallback."""

from __future__ import annotations

import json
import re
from typing import Any

import requests

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def mock_llm_response(prompt: str, task: str = "script") -> dict[str, Any]:
    """Return deterministic local content when no API key is configured."""
    title_match = re.search(r"Title:\s*(.+)", prompt)
    title = title_match.group(1).strip() if title_match else "AI Agent Browser Tool Trend"
    title = title[:56]
    script = (
        f"Do not scroll yet. {title} is not just another AI headline; it is a signal that creator workflows are changing.\n\n"
        "Here is the background: creators are drowning in new tools, but only a few trends are worth turning into content.\n\n"
        "First, this trend has a clear practical use case, so viewers can understand it quickly.\n"
        "Second, it connects to real creator pain points: research, scripting, editing, and publishing speed.\n"
        "Third, it gives you a useful angle: do not just report the launch, show what changes in the workflow.\n\n"
        "The viewer benefit is simple: they can decide whether this trend is worth their time without reading ten different sources.\n\n"
        "If you want faster breakdowns of AI tools and creator workflows, follow for the next one."
    )
    if task == "rewrite":
        script = (
            f"Stop for a second. {title} may be one of those small trends that quietly changes how creators work.\n\n"
            "The key context is this: creators do not need more hype. They need to know whether a trend can save time, create better content, or open a new angle.\n\n"
            "First, this trend is easy to explain visually.\n"
            "Second, it has a clear workflow use case.\n"
            "Third, it gives the audience a next step instead of just a headline.\n\n"
            "By the end, viewers should know what it is, why it matters, and whether they should try it.\n\n"
            "Follow if you want practical AI trend breakdowns without the noise."
        )
    return {
        "title": title,
        "description": "A concise breakdown of why this trend matters for creators and what to do next.",
        "tags": ["AI Tools", "Creator Workflow", "Short Video", "Automation"],
        "script": script,
    }


class LLMClient:
    """Minimal multi-provider client with safe mock fallback."""

    def __init__(self) -> None:
        self.provider = settings.llm_provider

    def generate_json(self, prompt: str, task: str = "script") -> dict[str, Any]:
        """Generate JSON-like content from the configured LLM provider."""
        try:
            if self.provider == "openai" and settings.openai_api_key:
                return self._call_openai(prompt)
            if self.provider == "deepseek" and settings.deepseek_api_key:
                return self._call_deepseek(prompt)
            if self.provider == "qwen" and settings.qwen_api_key:
                return self._call_qwen(prompt)
        except Exception as exc:
            logger.warning("LLM provider failed, using mock response: %s", exc)
        return mock_llm_response(prompt, task=task)

    def _chat_request(self, url: str, api_key: str, model: str, prompt: str) -> dict[str, Any]:
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a short-video content strategist. Return JSON only."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
            },
            timeout=40,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    def _call_openai(self, prompt: str) -> dict[str, Any]:
        return self._chat_request("https://api.openai.com/v1/chat/completions", settings.openai_api_key, settings.llm_model, prompt)

    def _call_deepseek(self, prompt: str) -> dict[str, Any]:
        return self._chat_request("https://api.deepseek.com/chat/completions", settings.deepseek_api_key, settings.llm_model, prompt)

    def _call_qwen(self, prompt: str) -> dict[str, Any]:
        return self._chat_request("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", settings.qwen_api_key, settings.llm_model, prompt)
