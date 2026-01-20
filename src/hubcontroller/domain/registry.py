from __future__ import annotations

from datetime import datetime  
from dataclasses import dataclass
from hubcontroller.domain.commands import Command, CommandStatus
from datetime import datetime, timezone

now = datetime.now(timezone.utc)

@dataclass(slots=True)
class CommandRecord:
        command: Command
        status: CommandStatus
        received_at: datetime
        accepted_at: datetime | None
        executed_at: datetime | None
        rejected_at: datetime | None
        timeout_at: datetime | None
        failed_at: datetime | None


class CommandRegistry:
    def __init__(self, accept_timeout_s: float = 3.0, exec_timeout_s: float = 80.0, ttl_s: float = 600.0):
        self.accept_timeout_s = accept_timeout_s  # seconds
        self.exec_timeout_s = exec_timeout_s # seconds
        self.ttl_s = ttl_s # seconds
        self._by_command_id: dict[str, CommandRecord] = {}
        
    def on_received(self, cmd: Command) -> tuple[CommandRecord, bool]:
        if cmd.command_id in self._by_command_id:
            return (self._by_command_id[cmd.command_id], False)
        else:
            self._by_command_id[cmd.command_id] = CommandRecord(command= cmd, status= CommandStatus.RECEIVED, received_at= self.now_utc())
            return (self._by_command_id[cmd.command_id], True)

    def now_utc() -> datetime:
        return datetime.now(timezone.utc)