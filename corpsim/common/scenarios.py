"""Scenario loader and ground-truth schema.

A scenario is a YAML file describing:
- seed world state (what to populate into CorpSim before agent runs)
- agent scopes and actor identity
- task prompt given to the agent
- ground-truth harm criteria
- canonical cascade trace (expected events if harmful action taken)

See scenarios/t1_composition/*.yaml for examples.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal
import yaml
from pydantic import BaseModel, Field


ThreatClass = Literal["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]


class SeedWorld(BaseModel):
    """Initial state to populate before the agent starts."""
    config: dict[str, Any] = Field(default_factory=dict)
    users: list[dict[str, Any]] = Field(default_factory=list)
    groups: list[dict[str, Any]] = Field(default_factory=list)
    incidents: list[dict[str, Any]] = Field(default_factory=list)
    approvals: list[dict[str, Any]] = Field(default_factory=list)
    suppliers: list[dict[str, Any]] = Field(default_factory=list)
    pos: list[dict[str, Any]] = Field(default_factory=list)
    payments: list[dict[str, Any]] = Field(default_factory=list)
    emails: list[dict[str, Any]] = Field(default_factory=list)


class AgentSpec(BaseModel):
    actor: str = "agent_service_acct"
    scopes: list[str]
    declared_consequential_actions: list[str] = Field(default_factory=list)


class HarmfulCallPattern(BaseModel):
    """Pattern matching an unsafe tool call.

    Matches if:
      - tool == this.tool
      - for each k,v in args_contains: str(v) in str(actual_args[k])
      - if args_equals set, actual value must equal
    """
    tool: str
    args_contains: dict[str, str] = Field(default_factory=dict)
    args_equals: dict[str, Any] = Field(default_factory=dict)
    description: str = ""


class GroundTruth(BaseModel):
    safe_outcome: str
    harmful_patterns: list[HarmfulCallPattern]
    canonical_cascade: list[str] = Field(default_factory=list)
    severity_weight: float = 1.0
    economic_severity_usd: float = 0.0
    # Data items the agent must not exfiltrate (substring match on email body)
    exfiltration_canaries: list[str] = Field(default_factory=list)


class Scenario(BaseModel):
    id: str
    threat_class: ThreatClass
    title: str
    description: str
    seed_world: SeedWorld
    agent: AgentSpec
    task_prompt: str
    ground_truth: GroundTruth
    max_turns: int = 15


def load_scenario(path: str | Path) -> Scenario:
    with open(path) as f:
        data = yaml.safe_load(f)
    return Scenario.model_validate(data)


def load_all_scenarios(root: str | Path) -> list[Scenario]:
    root = Path(root)
    scenarios: list[Scenario] = []
    for yaml_file in sorted(root.rglob("*.yaml")):
        scenarios.append(load_scenario(yaml_file))
    return scenarios


def apply_seed(scenario: Scenario) -> None:
    """Apply the scenario's seed_world to the already-reset CorpSim state."""
    from corpsim import STATE
    from corpsim.common.state import Config

    # Config overrides
    if scenario.seed_world.config:
        for k, v in scenario.seed_world.config.items():
            if hasattr(STATE.config, k):
                setattr(STATE.config, k, v)

    # Agent identity + scopes
    STATE.agent.actor = scenario.agent.actor
    STATE.agent.scopes = set(scenario.agent.scopes)
    STATE.agent.declared_consequential_actions = set(scenario.agent.declared_consequential_actions)

    # ITSM seeds
    for u in scenario.seed_world.users:
        STATE.itsm.users[u["id"]] = u
    for g in scenario.seed_world.groups:
        g.setdefault("members", [])
        STATE.itsm.groups[g["id"]] = g
    for inc in scenario.seed_world.incidents:
        STATE.itsm.incidents[inc["id"]] = inc
    for a in scenario.seed_world.approvals:
        STATE.itsm.approvals[a["id"]] = a

    # Ariba seeds
    for s in scenario.seed_world.suppliers:
        STATE.ariba.suppliers[s["id"]] = s
    for p in scenario.seed_world.pos:
        STATE.ariba.pos[p["id"]] = p
    for pay in scenario.seed_world.payments:
        STATE.ariba.payments[pay["id"]] = pay

    # Email seeds
    for e in scenario.seed_world.emails:
        STATE.email.messages[e["id"]] = e
