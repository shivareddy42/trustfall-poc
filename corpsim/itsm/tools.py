"""ITSM simulator — ServiceNow-inspired. 8 tool endpoints."""
from __future__ import annotations

from typing import Any
from corpsim.common.state import STATE
from corpsim.common.types import Event, EventKind, Severity, System, ToolCall, new_id, now_iso
from corpsim.eventbus.bus import BUS


REQUIRED_SCOPES = {
    "itsm.list_incidents": "itsm.incident.read",
    "itsm.get_incident": "itsm.incident.read",
    "itsm.create_incident": "itsm.incident.write",
    "itsm.update_incident": "itsm.incident.write",
    "itsm.list_approvals": "itsm.approval.read",
    "itsm.get_user": "itsm.user.read",
    "itsm.search_users": "itsm.user.read",
    "itsm.grant_group_membership": "itsm.identity.write",
}


def _check_scope(tool: str) -> None:
    needed = REQUIRED_SCOPES.get(tool)
    if needed and needed not in STATE.agent.scopes:
        raise PermissionError(f"scope {needed} required for {tool}")


def _record_tool_call(tool: str, args: dict[str, Any], result: Any = None, error: str | None = None) -> ToolCall:
    tc = ToolCall(
        actor=STATE.agent.actor,
        system=System.ITSM,
        tool=tool,
        args=args,
        result={"value": result} if not isinstance(result, dict) else result,
        error=error,
    )
    BUS.record_tool_call(tc)
    return tc


def list_incidents(state: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    _check_scope("itsm.list_incidents")
    results = list(STATE.itsm.incidents.values())
    if state:
        results = [r for r in results if r.get("state") == state]
    results = results[:limit]
    _record_tool_call("itsm.list_incidents", {"state": state, "limit": limit}, result={"items": results})
    return results


def get_incident(incident_id: str) -> dict[str, Any]:
    _check_scope("itsm.get_incident")
    inc = STATE.itsm.incidents.get(incident_id)
    _record_tool_call("itsm.get_incident", {"incident_id": incident_id}, result=inc)
    if not inc:
        raise KeyError(f"incident {incident_id} not found")
    return inc


def create_incident(short_description: str, description: str = "", priority: int = 3) -> dict[str, Any]:
    _check_scope("itsm.create_incident")
    iid = new_id("INC")
    inc = {
        "id": iid,
        "short_description": short_description,
        "description": description,
        "priority": priority,
        "state": "new",
        "created_at": now_iso(),
        "created_by": STATE.agent.actor,
    }
    STATE.itsm.incidents[iid] = inc
    _record_tool_call("itsm.create_incident", {"short_description": short_description, "priority": priority}, result=inc)
    BUS.emit(Event(
        system=System.ITSM, kind=EventKind.CREATE, entity_type="incident",
        entity_id=iid, actor=STATE.agent.actor, fields_after=dict(inc),
    ))
    return inc


def update_incident(incident_id: str, **changes: Any) -> dict[str, Any]:
    _check_scope("itsm.update_incident")
    inc = STATE.itsm.incidents.get(incident_id)
    if not inc:
        raise KeyError(f"incident {incident_id} not found")
    before = dict(inc)
    inc.update(changes)
    inc["updated_at"] = now_iso()
    _record_tool_call("itsm.update_incident", {"incident_id": incident_id, **changes}, result=inc)
    BUS.emit(Event(
        system=System.ITSM, kind=EventKind.UPDATE, entity_type="incident",
        entity_id=incident_id, actor=STATE.agent.actor,
        fields_before=before, fields_after=dict(inc),
    ))
    return inc


def list_approvals(approver: str | None = None, status: str = "pending") -> list[dict[str, Any]]:
    _check_scope("itsm.list_approvals")
    results = [a for a in STATE.itsm.approvals.values() if a.get("status") == status]
    if approver:
        results = [a for a in results if a.get("approver") == approver]
    _record_tool_call("itsm.list_approvals", {"approver": approver, "status": status}, result={"items": results})
    return results


def get_user(user_id: str) -> dict[str, Any]:
    _check_scope("itsm.get_user")
    u = STATE.itsm.users.get(user_id)
    _record_tool_call("itsm.get_user", {"user_id": user_id}, result=u)
    if not u:
        raise KeyError(f"user {user_id} not found")
    return u


def search_users(query: str) -> list[dict[str, Any]]:
    _check_scope("itsm.search_users")
    q = query.lower()
    results = [u for u in STATE.itsm.users.values()
               if q in u.get("name", "").lower() or q in u.get("email", "").lower()]
    _record_tool_call("itsm.search_users", {"query": query}, result={"items": results})
    return results


def grant_group_membership(user_id: str, group_id: str) -> dict[str, Any]:
    _check_scope("itsm.grant_group_membership")
    u = STATE.itsm.users.get(user_id)
    g = STATE.itsm.groups.get(group_id)
    if not u or not g:
        raise KeyError("user or group not found")
    members = g.setdefault("members", [])
    if user_id not in members:
        members.append(user_id)
    result = {"user_id": user_id, "group_id": group_id, "members": members}
    _record_tool_call("itsm.grant_group_membership", {"user_id": user_id, "group_id": group_id}, result=result)
    BUS.emit(Event(
        system=System.ITSM, kind=EventKind.ACCESS_GRANT, entity_type="group_membership",
        entity_id=f"{user_id}@{group_id}", actor=STATE.agent.actor,
        fields_after={"user_id": user_id, "group": group_id},
        severity=Severity.HIGH,
    ))
    return result
