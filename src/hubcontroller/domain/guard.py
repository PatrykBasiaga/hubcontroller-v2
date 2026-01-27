from enum import Enum
from dataclasses import dataclass

from hubcontroller.domain.hub_state import HubStateSnapshot, HubMode, ExecutionState
from hubcontroller.domain.commands import Command

class GuardDecisionReason(Enum):
    SAFETY_STOP_ACTIVE = "safety_stop_active"
    HUB_ERROR = "hub_error"
    HUB_STATE_UNKNOWN = "hub_state_unknown"
    HUB_BUSY = "hub_busy"
    ACTION_NEEDED = "action_needed"

@dataclass(frozen=True, slots=True)
class GuardDecision:
    allowed: bool = True
    reason: str | None = None


allowed_in_error = {"fault_ack"}
allowed_in_unknown = {"safety_ack"}
allowed_in_safety_stop = {"safety_ack"}
allowed_in_cycle_active = {"cycle_off"}
allowed_in_cycle_ready = {"start_cycle", "stop_cycle"}
allowed_in_homing_active = {"start_homing", "stop_homing"}
allowed_in_homing_ready = {"start_homing", "stop_homing"}
allowed_in_cycle = {"cycle_off"}


class Guard:
    def check(self, command: Command, hub_state_snapshot: HubStateSnapshot) -> GuardDecision:
        if hub_state_snapshot is None or hub_state_snapshot.mode == HubMode.UNKNOWN:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.HUB_STATE_UNKNOWN.value)
        elif hub_state_snapshot.mode == HubMode.SAFETY_STOP:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.SAFETY_STOP_ACTIVE.value)
        elif hub_state_snapshot.mode == HubMode.ERROR and not command.action in allowed_in_error:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.HUB_ERROR.value)
        elif hub_state_snapshot.mode == HubMode.HOMING_ACTIVE:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.HUB_BUSY.value)
        elif hub_state_snapshot.mode == HubMode.HOMING_READY or hub_state_snapshot.mode == HubMode.CYCLE_READY:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.ACTION_NEEDED.value)
        else:
            return GuardDecision(allowed=True, reason=None)
