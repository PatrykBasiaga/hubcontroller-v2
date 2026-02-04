from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Command:
    command_id: str
    command_type: str
    payload: Mapping[str, Any]


class CommandStatus(str, Enum):
    RECEIVED = "received"
    DISPATCHED = "dispatched"
    ACCEPTED = "accepted"
    EXECUTED = "executed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    FAILED = "failed"

class CommandIds(str, Enum):
    HOMING_ACTIVE = "homing_active"
    HOMING_READY = "homing_ready"
    CYCLE_ACTIVE = "cycle_active"
    CYCLE_READY = "cycle_ready"
    SAFETY_STOP = "safety_stop"
    ERROR = "error"
    UNKNOWN = "unknown"
    IDLE = "idle"
    EXECUTING = "executing"
    ACTION_NEEDED = "action_needed"
    FAILED = "failed"
