"""OpenAI baseline runner — wraps chat.completions into the AgentRunner protocol."""
from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI


class OpenAIRunner:
    def __init__(self, model: str = "gpt-5.3", temperature: float = 0.0,
                 api_key: str | None = None) -> None:
        self.name = model
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))

    def step(self, messages: list[dict[str, Any]], tools_spec: list[dict[str, Any]]
             ) -> dict[str, Any]:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools_spec,
            tool_choice="auto",
            temperature=self.temperature,
        )
        choice = resp.choices[0]
        msg = choice.message
        out: dict[str, Any] = {
            "content": msg.content,
            "tool_calls": [],
            "stop": choice.finish_reason == "stop",
        }
        if msg.tool_calls:
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                out["tool_calls"].append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": args,
                })
        return out


class MockRunner:
    """Deterministic mock runner for smoke tests.

    Returns a scripted sequence of tool-call / stop outputs regardless of input.
    """

    def __init__(self, script: list[dict[str, Any]], name: str = "mock") -> None:
        self.script = list(script)
        self.name = name

    def step(self, messages: list[dict[str, Any]], tools_spec: list[dict[str, Any]]
             ) -> dict[str, Any]:
        if not self.script:
            return {"content": "done", "tool_calls": [], "stop": True}
        return self.script.pop(0)
