"""Baseline runners.

Imports are lazy so running offline tests with only MockRunner does not
require the openai or anthropic SDKs to be installed.
"""
from __future__ import annotations

from typing import Any


class MockRunner:
    """Deterministic mock runner for smoke tests.

    Returns a scripted sequence of tool-call / stop outputs.
    """

    def __init__(self, script: list[dict[str, Any]], name: str = "mock") -> None:
        self.script = list(script)
        self.name = name

    def step(self, messages: list[dict[str, Any]], tools_spec: list[dict[str, Any]]
             ) -> dict[str, Any]:
        if not self.script:
            return {"content": "done", "tool_calls": [], "stop": True}
        return self.script.pop(0)


def __getattr__(name: str):
    if name == "OpenAIRunner":
        from baselines.openai_runner import OpenAIRunner
        return OpenAIRunner
    if name == "AnthropicRunner":
        from baselines.anthropic_runner import AnthropicRunner
        return AnthropicRunner
    raise AttributeError(f"module 'baselines' has no attribute {name!r}")


__all__ = ["MockRunner", "OpenAIRunner", "AnthropicRunner"]
