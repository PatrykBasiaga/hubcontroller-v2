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


allowed_in_error = {"fault_ack", "safety_stop", "machine_off"}
allowed_in_unknown = {"machine_on", "machine_off", "fault_ack", "safety_ack", "safety_stop"}
allowed_in_safety_stop = {"safety_ack", "machine_off", "safety_stop"}
allowed_in_cycle_active = {"stop_cycle", "machine_off", "safety_stop",
                           "prepare_to_start", "uav_started", "perform_diagnostic", "diagnostic_ok", "diagnostic_nok", 
                           "uav_landed", "hide_in_hub", "request_to_land", "load_battery", "unload_battery",
                           "load_uav_to_docks", "unload_uav_from_docks","start_mission", "abort_mission"}
allowed_in_cycle_ready = {"start_cycle", "machine_off", "safety_stop"}
allowed_in_homing_active = {"stop_homing", "machine_off", "safety_stop"}
allowed_in_homing_ready = {"start_homing", "machine_off", "safety_stop"}


class Guard:
    def check(self, command: Command, hub_state_snapshot: HubStateSnapshot) -> GuardDecision:
        if hub_state_snapshot is None or (hub_state_snapshot.mode == HubMode.UNKNOWN and command.command_type not in allowed_in_unknown):
            return GuardDecision(allowed=False, reason=GuardDecisionReason.HUB_STATE_UNKNOWN.value)
        elif hub_state_snapshot.mode == HubMode.SAFETY_STOP and command.command_type not in allowed_in_safety_stop:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.SAFETY_STOP_ACTIVE.value)
        elif hub_state_snapshot.mode == HubMode.ERROR and command.command_type not in allowed_in_error:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.HUB_ERROR.value)
        elif hub_state_snapshot.mode == HubMode.HOMING_ACTIVE and command.command_type not in allowed_in_homing_active:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.HUB_BUSY.value)
        elif hub_state_snapshot.mode == HubMode.HOMING_READY and command.command_type not in allowed_in_homing_ready:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.ACTION_NEEDED.value)
        elif hub_state_snapshot.mode == HubMode.CYCLE_READY and command.command_type not in allowed_in_cycle_ready:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.ACTION_NEEDED.value)
        elif hub_state_snapshot.mode == HubMode.CYCLE_ACTIVE and command.command_type not in allowed_in_cycle_active:
            return GuardDecision(allowed=False, reason=GuardDecisionReason.ACTION_NEEDED.value)
        else:
            return GuardDecision(allowed=True, reason=None)
