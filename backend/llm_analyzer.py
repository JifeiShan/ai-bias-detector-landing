"""
Optional OpenAI-compatible LLM review for inclusive-expression checks.

The rule engine remains the fast, deterministic first pass. This module is a
second pass used only when the backend has an API key configured. It is designed
for OpenAI-compatible chat-completions providers so the deployment can point at
OpenAI, Zhipu/GLM, MiMo, or another compatible endpoint via environment vars.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import httpx


SYSTEM_PROMPT = """你是一个中文招聘 JD / 公开文案的包容性表达审阅助手。
你的任务不是做法律结论，而是帮助发布者发现可能带来排除感、刻板印象或不必要性别绑定的表达，并给出更中性的改写建议。

请特别注意：
1. 显性限定：男性优先、女性优先、只招男/女、适合男/女等。
2. 职业-性别绑定：医生默认男性、护士默认女性、工程师默认男性、秘书默认女性等。
3. 能力/性格-性别绑定：把理性、技术、抗压、领导力默认绑定给男性；把细腻、沟通、支持、温柔默认绑定给女性。
4. 语境区分：如果文本是在表达“任何性别都可以”“医生可以是男性也可以是女性”，不要误报为偏见。
5. 输出要克制、可执行，避免道德审判口吻。

只输出 JSON，不要输出 Markdown，不要解释 JSON 外的内容。"""


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def llm_configured() -> bool:
    """Return True when an API key is present."""
    return bool(_get_env("LLM_API_KEY") or _get_env("OPENAI_API_KEY"))


def _extract_json(content: str) -> Dict[str, Any]:
    """Parse a JSON object, tolerating fenced-code output from some models."""
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def _coerce_case(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        score = float(item.get("bias_score", 0))
    except (TypeError, ValueError):
        score = 0.0

    template = str(item.get("template") or item.get("issue") or "大模型语境复核").strip()
    clue = str(item.get("male_output") or item.get("clue") or item.get("evidence") or "检测线索：需要复核语境").strip()
    suggestion = str(item.get("female_output") or item.get("suggestion") or item.get("rewrite") or "建议改为中性、基于职责/能力的表达").strip()

    if not template or score <= 0:
        return None

    return {
        "template": template[:120],
        "male_output": clue[:300],
        "female_output": suggestion[:300],
        "bias_score": max(0.0, min(score, 100.0)),
    }


async def analyze_bias_with_llm(text: str, model: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Run an optional LLM review. Return None when not configured or on failure.

    Environment variables:
    - LLM_API_KEY or OPENAI_API_KEY: required.
    - LLM_BASE_URL: optional, defaults to https://api.openai.com/v1.
    - LLM_MODEL: optional default model when request.model is absent.
    - LLM_TIMEOUT_SECONDS: optional, default 20.
    """
    api_key = _get_env("LLM_API_KEY") or _get_env("OPENAI_API_KEY")
    if not api_key:
        return None

    base_url = (_get_env("LLM_BASE_URL", "https://api.openai.com/v1") or "https://api.openai.com/v1").rstrip("/")
    selected_model = model or _get_env("LLM_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
    try:
        timeout = float(_get_env("LLM_TIMEOUT_SECONDS", "20") or "20")
    except ValueError:
        timeout = 20.0

    user_prompt = f"""请审阅下面这段中文文本，判断是否存在性别刻板印象或包容性表达风险。

文本：
{text[:6000]}

请输出严格 JSON，格式如下：
{{
  "overall_score": 0-100,
  "cases": [
    {{
      "template": "问题类型，短句",
      "male_output": "检测线索：引用或概括触发点",
      "female_output": "建议改写：给出更中性的表达",
      "bias_score": 0-100
    }}
  ],
  "recommendations": ["可执行建议1", "可执行建议2"]
}}

如果没有明显风险，overall_score 为 0-15，cases 为空，并解释建议继续保持中性表达。"""

    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = _extract_json(content)
    except Exception:
        # Never break the product when the model endpoint is unavailable.
        return None

    try:
        overall_score = float(parsed.get("overall_score", 0))
    except (TypeError, ValueError):
        overall_score = 0.0

    cases: List[Dict[str, Any]] = []
    for item in parsed.get("cases", []) or []:
        if isinstance(item, dict):
            case = _coerce_case(item)
            if case:
                cases.append(case)

    recommendations = [str(item).strip()[:300] for item in parsed.get("recommendations", []) or [] if str(item).strip()]

    return {
        "overall_score": max(0.0, min(overall_score, 100.0)),
        "cases": cases[:5],
        "recommendations": recommendations[:5],
        "model_used": selected_model,
    }
