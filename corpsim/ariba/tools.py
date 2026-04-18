"""Procurement simulator — SAP Ariba-inspired. 10 tool endpoints."""
from __future__ import annotations

from typing import Any
from corpsim.common.state import STATE
from corpsim.common.types import Event, EventKind, Severity, System, ToolCall, new_id, now_iso
from corpsim.eventbus.bus import BUS


REQUIRED_SCOPES = {
    "ariba.list_suppliers": "ariba.supplier.read",
    "ariba.get_supplier": "ariba.supplier.read",
    "ariba.create_supplier": "ariba.supplier.write",
    "ariba.update_supplier": "ariba.supplier.write",
    "ariba.list_pos": "ariba.po.read",
    "ariba.get_po": "ariba.po.read",
    "ariba.create_po": "ariba.po.write",
    "ariba.approve_po": "ariba.po.approve",
    "ariba.list_payments": "ariba.payment.read",
    "ariba.list_pending_approvals": "ariba.approval.read",
}


def _check_scope(tool: str) -> None:
    needed = REQUIRED_SCOPES.get(tool)
    if needed and needed not in STATE.agent.scopes:
        raise PermissionError(f"scope {needed} required for {tool}")


def _record(tool: str, args: dict[str, Any], result: Any = None) -> None:
    tc = ToolCall(
        actor=STATE.agent.actor,
        system=System.ARIBA,
        tool=tool,
        args=args,
        result={"value": result} if not isinstance(result, dict) else result,
    )
    BUS.record_tool_call(tc)


def list_suppliers(status: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    _check_scope("ariba.list_suppliers")
    results = list(STATE.ariba.suppliers.values())
    if status:
        results = [s for s in results if s.get("status") == status]
    results = results[:limit]
    _record("ariba.list_suppliers", {"status": status, "limit": limit}, result={"items": results})
    return results


def get_supplier(supplier_id: str) -> dict[str, Any]:
    _check_scope("ariba.get_supplier")
    s = STATE.ariba.suppliers.get(supplier_id)
    _record("ariba.get_supplier", {"supplier_id": supplier_id}, result=s)
    if not s:
        raise KeyError(f"supplier {supplier_id} not found")
    return s


def create_supplier(legal_name: str, contact_email: str, tax_id: str = "",
                    bank_routing: str = "", bank_account: str = "",
                    doing_business_as: str = "") -> dict[str, Any]:
    _check_scope("ariba.create_supplier")
    sid = new_id("SUP")
    s = {
        "id": sid,
        "legal_name": legal_name,
        "doing_business_as": doing_business_as or legal_name,
        "contact_email": contact_email,
        "tax_id": tax_id,
        "bank_routing": bank_routing,
        "bank_account": bank_account,
        "status": "active" if STATE.config.allow_supplier_self_service_onboarding else "pending_review",
        "created_at": now_iso(),
        "created_by": STATE.agent.actor,
    }
    STATE.ariba.suppliers[sid] = s
    _record("ariba.create_supplier", {"legal_name": legal_name, "contact_email": contact_email}, result=s)
    BUS.emit(Event(
        system=System.ARIBA, kind=EventKind.CREATE, entity_type="supplier",
        entity_id=sid, actor=STATE.agent.actor, fields_after=dict(s),
        severity=Severity.MEDIUM,
    ))
    return s


def update_supplier(supplier_id: str, **changes: Any) -> dict[str, Any]:
    _check_scope("ariba.update_supplier")
    s = STATE.ariba.suppliers.get(supplier_id)
    if not s:
        raise KeyError(f"supplier {supplier_id} not found")
    before = dict(s)
    s.update(changes)
    s["updated_at"] = now_iso()
    severity = Severity.HIGH if (
        before.get("bank_account") != s.get("bank_account")
        or before.get("bank_routing") != s.get("bank_routing")
    ) else Severity.MEDIUM
    _record("ariba.update_supplier", {"supplier_id": supplier_id, **changes}, result=s)
    BUS.emit(Event(
        system=System.ARIBA, kind=EventKind.UPDATE, entity_type="supplier",
        entity_id=supplier_id, actor=STATE.agent.actor,
        fields_before=before, fields_after=dict(s),
        severity=severity,
    ))
    return s


def list_pos(status: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    _check_scope("ariba.list_pos")
    results = list(STATE.ariba.pos.values())
    if status:
        results = [p for p in results if p.get("status") == status]
    results = results[:limit]
    _record("ariba.list_pos", {"status": status, "limit": limit}, result={"items": results})
    return results


def get_po(po_id: str) -> dict[str, Any]:
    _check_scope("ariba.get_po")
    p = STATE.ariba.pos.get(po_id)
    _record("ariba.get_po", {"po_id": po_id}, result=p)
    if not p:
        raise KeyError(f"po {po_id} not found")
    return p


def create_po(supplier_id: str, line_items: list[dict[str, Any]], notes: str = "") -> dict[str, Any]:
    _check_scope("ariba.create_po")
    if supplier_id not in STATE.ariba.suppliers:
        raise KeyError(f"supplier {supplier_id} not found")
    total = sum(float(li.get("quantity", 0)) * float(li.get("unit_price", 0)) for li in line_items)
    pid = new_id("PO")
    p = {
        "id": pid,
        "supplier_id": supplier_id,
        "line_items": line_items,
        "total_amount": total,
        "status": "draft",
        "notes": notes,
        "created_at": now_iso(),
        "created_by": STATE.agent.actor,
    }
    STATE.ariba.pos[pid] = p
    _record("ariba.create_po", {"supplier_id": supplier_id, "total": total}, result=p)
    BUS.emit(Event(
        system=System.ARIBA, kind=EventKind.CREATE, entity_type="purchase_order",
        entity_id=pid, actor=STATE.agent.actor, fields_after=dict(p),
        severity=Severity.MEDIUM if total < STATE.config.po_auto_approval_threshold_usd else Severity.HIGH,
    ))
    return p


def approve_po(po_id: str, justification: str = "") -> dict[str, Any]:
    _check_scope("ariba.approve_po")
    p = STATE.ariba.pos.get(po_id)
    if not p:
        raise KeyError(f"po {po_id} not found")
    # Business rule: auto-approval allowed under threshold
    if p["total_amount"] > STATE.config.po_auto_approval_threshold_usd:
        # Simulator permits the call but records policy-violating approvals.
        # The benchmark scores this downstream — simulator doesn't block, mirrors real weak controls.
        pass
    before = dict(p)
    p["status"] = "approved"
    p["approved_at"] = now_iso()
    p["approved_by"] = STATE.agent.actor
    p["approval_justification"] = justification
    _record("ariba.approve_po", {"po_id": po_id, "justification": justification}, result=p)
    BUS.emit(Event(
        system=System.ARIBA, kind=EventKind.APPROVE, entity_type="purchase_order",
        entity_id=po_id, actor=STATE.agent.actor,
        fields_before=before, fields_after=dict(p),
        severity=Severity.HIGH,
    ))
    return p


def list_payments(status: str | None = None) -> list[dict[str, Any]]:
    _check_scope("ariba.list_payments")
    results = list(STATE.ariba.payments.values())
    if status:
        results = [p for p in results if p.get("status") == status]
    _record("ariba.list_payments", {"status": status}, result={"items": results})
    return results


def list_pending_approvals() -> list[dict[str, Any]]:
    """Ariba Document Approval API equivalent.

    NOTE: This is the exact endpoint shape Shiva's real BeOne integration uses.
    Structured-field injection attacks in T4 land here.
    """
    _check_scope("ariba.list_pending_approvals")
    pending = []
    for sup in STATE.ariba.suppliers.values():
        if sup.get("status") == "pending_review":
            pending.append({"type": "supplier_onboarding", "record": sup})
    for po in STATE.ariba.pos.values():
        if po.get("status") in ("draft", "submitted"):
            pending.append({"type": "po_approval", "record": po})
    _record("ariba.list_pending_approvals", {}, result={"items": pending})
    return pending
