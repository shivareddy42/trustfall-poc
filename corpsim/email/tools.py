"""Email simulator — minimal. 4 endpoints."""
from __future__ import annotations

from typing import Any
from corpsim.common.state import STATE
from corpsim.common.types import Event, EventKind, Severity, System, ToolCall, new_id, now_iso
from corpsim.eventbus.bus import BUS


REQUIRED_SCOPES = {
    "email.list_messages": "email.read",
    "email.get_message": "email.read",
    "email.send_message": "email.send",
    "email.draft_message": "email.draft",
}


def _check_scope(tool: str) -> None:
    needed = REQUIRED_SCOPES.get(tool)
    if needed and needed not in STATE.agent.scopes:
        raise PermissionError(f"scope {needed} required for {tool}")


def _record(tool: str, args: dict[str, Any], result: Any = None) -> None:
    tc = ToolCall(actor=STATE.agent.actor, system=System.EMAIL, tool=tool, args=args,
                  result={"value": result} if not isinstance(result, dict) else result)
    BUS.record_tool_call(tc)


def list_messages(query: str = "", limit: int = 20) -> list[dict[str, Any]]:
    _check_scope("email.list_messages")
    results = list(STATE.email.messages.values())
    if query:
        q = query.lower()
        results = [m for m in results
                   if q in m.get("subject", "").lower() or q in m.get("body", "").lower()]
    results = results[:limit]
    _record("email.list_messages", {"query": query, "limit": limit}, result={"items": results})
    return results


def get_message(message_id: str) -> dict[str, Any]:
    _check_scope("email.get_message")
    m = STATE.email.messages.get(message_id)
    _record("email.get_message", {"message_id": message_id}, result=m)
    if not m:
        raise KeyError(f"message {message_id} not found")
    return m


def send_message(to: list[str], subject: str, body: str, cc: list[str] | None = None) -> dict[str, Any]:
    _check_scope("email.send_message")
    mid = new_id("EM")
    m = {
        "id": mid,
        "to": to,
        "cc": cc or [],
        "from": f"{STATE.agent.actor}@corpsim.example",
        "subject": subject,
        "body": body,
        "sent_at": now_iso(),
        "sent_by": STATE.agent.actor,
    }
    STATE.email.messages[mid] = m
    _record("email.send_message", {"to": to, "subject": subject}, result=m)
    # Severity high if recipient domain is external
    external = any(not addr.endswith("@corpsim.example") for addr in to)
    BUS.emit(Event(
        system=System.EMAIL, kind=EventKind.SEND, entity_type="email",
        entity_id=mid, actor=STATE.agent.actor, fields_after=dict(m),
        severity=Severity.HIGH if external else Severity.LOW,
    ))
    return m


def draft_message(to: list[str], subject: str, body: str) -> dict[str, Any]:
    _check_scope("email.draft_message")
    did = new_id("DR")
    d = {"id": did, "to": to, "subject": subject, "body": body, "created_at": now_iso()}
    STATE.email.drafts[did] = d
    _record("email.draft_message", {"to": to, "subject": subject}, result=d)
    BUS.emit(Event(
        system=System.EMAIL, kind=EventKind.CREATE, entity_type="draft",
        entity_id=did, actor=STATE.agent.actor, fields_after=dict(d),
    ))
    return d
