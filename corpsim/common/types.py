"""Shared types across CorpSim."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field
import uuid


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


class System(str, Enum):
    ITSM = "itsm"
    ARIBA = "ariba"
    EMAIL = "email"
    CMDB = "cmdb"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventKind(str, Enum):
    # writes
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    # approvals
    APPROVE = "approve"
    REJECT = "reject"
    # comms
    SEND = "send"
    # security
    ACCESS_GRANT = "access_grant"
    ACCESS_REVOKE = "access_revoke"
    # auth
    AUTH = "auth"


class ToolCall(BaseModel):
    """Record of an agent tool invocation."""
    id: str = Field(default_factory=lambda: new_id("TC"))
    timestamp: str = Field(default_factory=now_iso)
    actor: str  # agent service acct
    system: System
    tool: str
    args: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None


class Event(BaseModel):
    """Typed event emitted on any state change. Drives cascade engine + metrics."""
    id: str = Field(default_factory=lambda: new_id("EV"))
    timestamp: str = Field(default_factory=now_iso)
    sim_clock: int = 0  # logical tick for deterministic ordering
    system: System
    kind: EventKind
    entity_type: str  # e.g. "supplier", "purchase_order"
    entity_id: str
    actor: str
    fields_before: dict[str, Any] | None = None
    fields_after: dict[str, Any] | None = None
    severity: Severity = Severity.INFO
    caused_by: str | None = None  # parent event id for cascades
    tool_call_id: str | None = None
    # For DL metric: would a default SIEM rule fire on this event?
    siem_alert: bool = False
    siem_rule: str | None = None


class CascadeRule(BaseModel):
    """Rule describing how one event propagates to downstream state changes."""
    name: str
    trigger_system: System
    trigger_entity: str
    trigger_kind: EventKind
    trigger_fields: list[str] = []  # only fire if these fields changed
    description: str
    # The cascade handler is resolved at runtime by name
    handler: str


class ScenarioLabel(BaseModel):
    """Ground truth for an adversarial scenario."""
    scenario_id: str
    threat_class: Literal["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]
    harmful_tool_calls: list[dict[str, Any]]  # patterns of forbidden calls
    safe_outcome_description: str
    canonical_cascade: list[str] = []  # expected event chain if harmful action taken
    severity_weight: float = 1.0  # multiplier for SWH
    economic_severity_usd: float = 0.0
