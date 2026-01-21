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
    ACCEPTED = "accepted"
    EXECUTED = "executed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    FAILED = "failed"
