"""Anthropic baseline runner."""
from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic


class AnthropicRunner:
    def __init__(self, model: str = "claude-opus-4-7", max_tokens: int = 2048,
                 api_key: str | None = None) -> None:
        self.name = model
        self.model = model
        self.max_tokens = max_tokens
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def step(self, messages: list[dict[str, Any]], tools_spec: list[dict[str, Any]]
             ) -> dict[str, Any]:
        # Anthropic uses a separate `system` field
        system_text = ""
        anth_messages: list[dict[str, Any]] = []
        for m in messages:
            if m["role"] == "system":
                system_text = m["content"]
            else:
                anth_messages.append(m)

        resp = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_text,
            messages=anth_messages,
            tools=tools_spec,
        )

        content_text = ""
        tool_calls: list[dict[str, Any]] = []
        raw_blocks: list[dict[str, Any]] = []
        for block in resp.content:
            if block.type == "text":
                content_text += block.text
                raw_blocks.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input or {},
                })
                raw_blocks.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        return {
            "content": content_text or None,
            "tool_calls": tool_calls,
            "raw_content": raw_blocks,
            "stop": resp.stop_reason in ("end_turn", "stop_sequence"),
        }
