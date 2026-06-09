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
    title_match = re.search(r"标题[:：]\s*(.+)", prompt)
    title = title_match.group(1).strip() if title_match else "AI Agent 浏览器插件正在变成新趋势"
    title = title[:40]

    script = (
        f"别急着划走，{title}可能正在改变内容创作者的工作流。\n\n"
        "先说背景：现在热点越来越多，但真正值得做成内容的，必须同时满足新鲜、可解释、对观众有用这三个条件。\n\n"
        "第一，它不是单纯的新闻，而是一个普通人可以理解、可以尝试、可以转化成行动的变化。\n"
        "第二，它连接了真实场景，比如效率提升、学习决策、工具选择或内容变现。\n"
        "第三，越早把它解释清楚，越容易建立账号的专业感和信任感。\n\n"
        "对观众的收益是：不用自己翻一堆资料，也能快速判断这个热点值不值得关注。\n\n"
        "如果你想持续看懂新工具和新趋势，关注我，下一条继续拆解。"
    )
    if task == "rewrite":
        script = (
            f"先别划走，{title}不是又一个普通热点，它更像是创作者工作流变化的信号。\n\n"
            "背景很简单：热点很多，但能做成好内容的热点，必须能回答一个问题：它和普通人有什么关系？\n\n"
            "第一，它有明确的新鲜感，适合用短视频快速解释。\n"
            "第二，它能连接真实使用场景，比如提效、学习、选工具和做内容。\n"
            "第三，它给创作者提供了一个清晰角度：不是追新闻，而是帮观众判断机会。\n\n"
            "看完这条，你至少能知道它值不值得继续关注，以及下一步该从哪里开始了解。\n\n"
            "想每天更快看懂新趋势，关注我，我们下一条继续拆。"
        )
    return {
        "title": title,
        "description": "用一分钟看懂热点价值、应用场景和创作者机会。",
        "tags": ["AI工具", "科技趋势", "短视频", "效率"],
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
                    {"role": "system", "content": "你是短视频内容制作专家，只输出 JSON。"},
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
