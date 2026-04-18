"""CorpSim — simulated enterprise environment for TRUSTFALL."""
from __future__ import annotations

from typing import Any, Callable
from corpsim import itsm, ariba, email
from corpsim.common.state import STATE, CorpState, reset_state
from corpsim.eventbus import BUS
from corpsim.eventbus.cascades import register_all_cascades, register_siem


ALL_TOOLS: dict[str, Callable[..., Any]] = {
    **itsm.TOOLS,
    **ariba.TOOLS,
    **email.TOOLS,
}


def reset_world() -> CorpState:
    """Reset all state + re-register cascades + SIEM. Called per scenario."""
    BUS.reset()
    state = reset_state()
    register_all_cascades(state)
    register_siem(state)
    return state


__all__ = [
    "ALL_TOOLS",
    "BUS",
    "STATE",
    "CorpState",
    "reset_world",
    "itsm",
    "ariba",
    "email",
]
