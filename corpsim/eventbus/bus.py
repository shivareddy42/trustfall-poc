"""Event bus — deterministic, single-process, in-memory.

All state changes across CorpSim systems MUST flow through here.
This is the instrumentation backbone for blast radius + detection latency.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable
from corpsim.common.types import Event, ToolCall


class EventBus:
    def __init__(self) -> None:
        self._events: list[Event] = []
        self._tool_calls: list[ToolCall] = []
        self._subscribers: dict[str, list[Callable[[Event], None]]] = defaultdict(list)
        self._sim_clock: int = 0
        self._current_tool_call_id: str | None = None
        self._current_root_event_id: str | None = None  # for cascade parent tracking

    @property
    def sim_clock(self) -> int:
        return self._sim_clock

    def tick(self) -> int:
        self._sim_clock += 1
        return self._sim_clock

    def subscribe(self, event_key: str, handler: Callable[[Event], None]) -> None:
        """event_key format: '<system>.<entity_type>.<kind>' or '*' for all."""
        self._subscribers[event_key].append(handler)

    def emit(self, event: Event) -> Event:
        event.sim_clock = self.tick()
        if self._current_tool_call_id and not event.tool_call_id:
            event.tool_call_id = self._current_tool_call_id
        if self._current_root_event_id and not event.caused_by:
            event.caused_by = self._current_root_event_id
        self._events.append(event)

        # Dispatch to subscribers (cascade handlers)
        keys = [
            "*",
            f"{event.system.value}.*.*",
            f"{event.system.value}.{event.entity_type}.*",
            f"{event.system.value}.{event.entity_type}.{event.kind.value}",
        ]
        # Track cascade parent — children emitted inside a handler inherit this root
        prev_root = self._current_root_event_id
        if prev_root is None:
            self._current_root_event_id = event.id
        try:
            for k in keys:
                for h in self._subscribers.get(k, []):
                    h(event)
        finally:
            self._current_root_event_id = prev_root
        return event

    def record_tool_call(self, tc: ToolCall) -> None:
        self._tool_calls.append(tc)
        self._current_tool_call_id = tc.id

    def clear_tool_call_context(self) -> None:
        self._current_tool_call_id = None
        self._current_root_event_id = None

    # --- Introspection for metrics ---

    def events(self) -> list[Event]:
        return list(self._events)

    def tool_calls(self) -> list[ToolCall]:
        return list(self._tool_calls)

    def events_caused_by(self, root_id: str) -> list[Event]:
        """Transitive closure of events cascading from root_id."""
        # BFS across caused_by chain
        descendants: set[str] = set()
        frontier = {root_id}
        while frontier:
            next_frontier: set[str] = set()
            for e in self._events:
                if e.caused_by in frontier and e.id not in descendants:
                    descendants.add(e.id)
                    next_frontier.add(e.id)
            frontier = next_frontier
        return [e for e in self._events if e.id in descendants]

    def first_alert(self) -> Event | None:
        for e in self._events:
            if e.siem_alert:
                return e
        return None

    def reset(self) -> None:
        self._events.clear()
        self._tool_calls.clear()
        self._subscribers.clear()
        self._sim_clock = 0
        self._current_tool_call_id = None
        self._current_root_event_id = None


# Module-level singleton — tests and harness reset between scenarios
BUS = EventBus()
