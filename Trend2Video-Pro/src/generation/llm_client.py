"""Unified LLM client with mock fallback."""

from __future__ import annotations

import json
from typing import Any

import requests

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def mock_llm_response(prompt: str, task: str = "script") -> dict[str, Any]:
    """Return deterministic local content when no API key is configured."""
    if task == "rewrite":
        return {
            "script": "别急着划走，这个趋势可能正在改变普通创作者的内容生产方式。\n\n它的背景很简单：用户需求正在从看热闹，转向快速判断一个新工具、新事件到底值不值得跟。\n\n第一，趋势本身有明确的新鲜感，适合用短视频快速解释。\n第二，它能连接真实场景，比如效率提升、创作变现或学习决策。\n第三，观众最关心的不是新闻本身，而是自己能不能马上用上。\n\n对你来说，最重要的收益是：少花时间追热点，多花时间判断机会。\n\n如果你也想每天更快看懂新趋势，记得关注，我会继续把复杂信息讲成能直接行动的内容。",
        }
    return {
        "title": "这个新趋势，正在改变内容创作者的工作流",
        "description": "用一分钟看懂热点价值、应用场景和创作者机会。",
        "tags": ["AI工具", "科技趋势", "短视频", "效率"],
        "script": "别急着划走，这个新趋势可能正在改变内容创作者的工作流。\n\n先说背景：现在热点越来越多，但真正值得做成内容的，必须同时满足新鲜、可解释、对观众有用这三个条件。\n\n第一个核心点，它不是单纯的新闻，而是一个可以被普通人理解和使用的变化。\n第二个核心点，它和效率、学习、创作或商业机会有关，所以观众看完会有行动方向。\n第三个核心点，越早解释清楚，越容易建立账号的专业感和信任感。\n\n对用户的收益是：你不用自己翻一堆资料，也能快速判断这个热点值不值得关注。\n\n如果你想持续看懂新工具和新趋势，关注我，下一条继续拆解。",
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
