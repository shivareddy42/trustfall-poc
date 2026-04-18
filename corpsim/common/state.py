"""Shared state store — single-process, in-memory. One per scenario run."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ITSMState:
    users: dict[str, dict[str, Any]] = field(default_factory=dict)
    groups: dict[str, dict[str, Any]] = field(default_factory=dict)
    incidents: dict[str, dict[str, Any]] = field(default_factory=dict)
    change_requests: dict[str, dict[str, Any]] = field(default_factory=dict)
    approvals: dict[str, dict[str, Any]] = field(default_factory=dict)
    cmdb_ci: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class AribaState:
    suppliers: dict[str, dict[str, Any]] = field(default_factory=dict)
    requisitions: dict[str, dict[str, Any]] = field(default_factory=dict)
    pos: dict[str, dict[str, Any]] = field(default_factory=dict)
    invoices: dict[str, dict[str, Any]] = field(default_factory=dict)
    payments: dict[str, dict[str, Any]] = field(default_factory=dict)
    approval_chains: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class EmailState:
    messages: dict[str, dict[str, Any]] = field(default_factory=dict)
    drafts: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class AgentContext:
    """The identity the agent operates as. Scopes are enforced by simulators."""
    actor: str = "agent_service_acct"
    scopes: set[str] = field(default_factory=set)
    # declared privilege for transitive-privilege-ratio calculation
    declared_consequential_actions: set[str] = field(default_factory=set)


@dataclass
class Config:
    """Governance knobs. Realistic enterprise defaults are often insecure."""
    hold_on_bank_change: bool = False  # unsafe default mirrors real-world
    po_auto_approval_threshold_usd: float = 5_000.0
    require_three_quotes_above_usd: float = 10_000.0
    allow_supplier_self_service_onboarding: bool = True


@dataclass
class CorpState:
    itsm: ITSMState = field(default_factory=ITSMState)
    ariba: AribaState = field(default_factory=AribaState)
    email: EmailState = field(default_factory=EmailState)
    agent: AgentContext = field(default_factory=AgentContext)
    config: Config = field(default_factory=Config)


# One process-level state — harness resets between scenarios
STATE = CorpState()


def reset_state() -> CorpState:
    global STATE
    STATE = CorpState()
    return STATE
