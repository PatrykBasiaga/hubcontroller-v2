from dataclasses import dataclass
from enum import Enum


class HubMode(str, Enum):
    ERROR = "error"
    UNKNOWN = "unknown"
    SAFETY_STOP = "safety_stop"
    CYCLE_ACTIVE = "cycle_active"
    CYCLE_READY = "cycle_ready"
    HOMING_ACTIVE = "homing_active"
    HOMING_READY = "homing_ready"


class ExecutionState(str, Enum):
    IDLE = "idle"
    EXECUTING = "executing"
    ACTION_NEEDED = "action_needed" 
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class HubStateSnapshot:
    mode: HubMode
    execution_state: ExecutionState
