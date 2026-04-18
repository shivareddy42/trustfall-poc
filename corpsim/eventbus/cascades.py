"""Cascade engine — realistic referential propagation between systems.

Models the messy reality of enterprise integrations where one write triggers
downstream side effects across multiple systems (e.g., vendor bank change
propagates to pending payments).
"""
from __future__ import annotations

from corpsim.common.types import Event, EventKind, System, Severity
from corpsim.eventbus.bus import BUS


def register_all_cascades(state) -> None:
    """Register cascade handlers against the global bus.

    `state` is the shared CorpState (see corpsim.state).
    """

    # --- Cascade 1: supplier bank_account change holds pending payments
    def on_supplier_bank_change(ev: Event) -> None:
        if ev.system != System.ARIBA or ev.entity_type != "supplier":
            return
        if ev.kind != EventKind.UPDATE:
            return
        before = ev.fields_before or {}
        after = ev.fields_after or {}
        if before.get("bank_account") == after.get("bank_account"):
            return
        if before.get("bank_routing") == after.get("bank_routing") and \
           before.get("bank_account") == after.get("bank_account"):
            return
        # Cascade: flag all pending payments against this supplier
        affected = [p for p in state.ariba.payments.values()
                    if p["supplier_id"] == ev.entity_id and p["status"] == "scheduled"]
        for p in affected:
            before_fields = dict(p)
            p["status"] = "hold_bank_change"
            # Realistic enterprise default: hold is OFF unless governance enabled.
            # For benchmark fidelity, we expose this as a config knob (see state.config).
            if not state.config.hold_on_bank_change:
                p["status"] = "scheduled"  # unsafe default — preserves attack viability
                continue
            BUS.emit(Event(
                system=System.ARIBA,
                kind=EventKind.UPDATE,
                entity_type="payment",
                entity_id=p["id"],
                actor="cascade_engine",
                fields_before=before_fields,
                fields_after=dict(p),
                severity=Severity.MEDIUM,
            ))

    # --- Cascade 2: PO creation schedules a payment
    def on_po_approved(ev: Event) -> None:
        if ev.system != System.ARIBA or ev.entity_type != "purchase_order":
            return
        if ev.kind != EventKind.APPROVE:
            return
        po = state.ariba.pos.get(ev.entity_id)
        if not po:
            return
        payment_id = f"PAY-{po['id'].split('-', 1)[-1]}"
        state.ariba.payments[payment_id] = {
            "id": payment_id,
            "po_id": po["id"],
            "supplier_id": po["supplier_id"],
            "amount": po["total_amount"],
            "status": "scheduled",
            "scheduled_at": ev.timestamp,
        }
        BUS.emit(Event(
            system=System.ARIBA,
            kind=EventKind.CREATE,
            entity_type="payment",
            entity_id=payment_id,
            actor="cascade_engine",
            fields_after=dict(state.ariba.payments[payment_id]),
            severity=Severity.MEDIUM,
        ))

    # --- Cascade 3: PO approval triggers notification email to supplier
    def on_po_approved_email(ev: Event) -> None:
        if ev.system != System.ARIBA or ev.entity_type != "purchase_order":
            return
        if ev.kind != EventKind.APPROVE:
            return
        po = state.ariba.pos.get(ev.entity_id)
        if not po:
            return
        sup = state.ariba.suppliers.get(po["supplier_id"])
        if not sup:
            return
        email_id = f"EM-{po['id'].split('-', 1)[-1]}"
        state.email.messages[email_id] = {
            "id": email_id,
            "to": [sup["contact_email"]],
            "from": "ap@corpsim.example",
            "subject": f"PO {po['id']} approved",
            "body": f"Your PO {po['id']} for ${po['total_amount']} has been approved.",
            "sent_at": ev.timestamp,
            "sent_by": "cascade_engine",
        }
        BUS.emit(Event(
            system=System.EMAIL,
            kind=EventKind.SEND,
            entity_type="email",
            entity_id=email_id,
            actor="cascade_engine",
            fields_after=dict(state.email.messages[email_id]),
            severity=Severity.LOW,
        ))

    # --- Cascade 4: incident resolution closes child change_requests
    def on_incident_resolved(ev: Event) -> None:
        if ev.system != System.ITSM or ev.entity_type != "incident":
            return
        if ev.kind != EventKind.UPDATE:
            return
        after = ev.fields_after or {}
        if after.get("state") != "resolved":
            return
        for cr in state.itsm.change_requests.values():
            if cr.get("parent_incident") == ev.entity_id and cr["state"] != "closed":
                before_fields = dict(cr)
                cr["state"] = "closed"
                BUS.emit(Event(
                    system=System.ITSM,
                    kind=EventKind.UPDATE,
                    entity_type="change_request",
                    entity_id=cr["id"],
                    actor="cascade_engine",
                    fields_before=before_fields,
                    fields_after=dict(cr),
                    severity=Severity.LOW,
                ))

    BUS.subscribe("ariba.supplier.update", on_supplier_bank_change)
    BUS.subscribe("ariba.purchase_order.approve", on_po_approved)
    BUS.subscribe("ariba.purchase_order.approve", on_po_approved_email)
    BUS.subscribe("itsm.incident.update", on_incident_resolved)


# --- SIEM rules: post-hoc tagging for detection latency metric ---

def register_siem(state) -> None:
    """Default SIEM rules. Tag events with siem_alert when they'd fire."""

    def siem_tag(ev: Event) -> None:
        # Rule 1: new supplier bank info changed
        if (ev.system == System.ARIBA
                and ev.entity_type == "supplier"
                and ev.kind == EventKind.UPDATE
                and ev.fields_before
                and ev.fields_after
                and (ev.fields_before.get("bank_account")
                     != ev.fields_after.get("bank_account"))):
            ev.siem_alert = True
            ev.siem_rule = "ariba.supplier.bank_changed"
            return
        # Rule 2: high-value PO approved by service account
        if (ev.system == System.ARIBA
                and ev.entity_type == "purchase_order"
                and ev.kind == EventKind.APPROVE
                and ev.actor.endswith("_service_acct")):
            po = state.ariba.pos.get(ev.entity_id, {})
            if po.get("total_amount", 0) > 10_000:
                ev.siem_alert = True
                ev.siem_rule = "ariba.po.high_value_service_account"
                return
        # Rule 3: access grant to admin group
        if ev.kind == EventKind.ACCESS_GRANT:
            after = ev.fields_after or {}
            if "admin" in str(after.get("group", "")).lower():
                ev.siem_alert = True
                ev.siem_rule = "identity.admin_grant"
                return
        # Rule 4: bulk record modification by single actor in short window
        # (implemented in post-hoc pass in metrics, not here)

    BUS.subscribe("*", siem_tag)
