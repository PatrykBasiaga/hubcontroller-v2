from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable

from hubcontroller.domain.commands import Command, CommandStatus

@dataclass(slots=True)
class CommandRecord:
    command: Command
    status: CommandStatus
    received_at: datetime
    accepted_at: datetime | None = None
    executed_at: datetime | None = None
    rejected_at: datetime | None = None
    timeout_at: datetime | None = None
    failed_at: datetime | None = None

    def is_terminal(self) -> bool:
        return self.status in {CommandStatus.EXECUTED, CommandStatus.REJECTED, CommandStatus.FAILED, CommandStatus.TIMEOUT}

class TransitionResult(str, Enum):
    OK = "ok"
    DUPLICATE = "duplicate"
    UNKNOWN_COMMAND = "unknown_command"
    INVALID_STATE = "invalid_state"
    TERMINAL = "terminal"

@dataclass(slots=True)
class Transition:
    record: CommandRecord | None
    result: TransitionResult
    changed: bool

class CommandRegistry:
    def __init__(self, accept_timeout_s: float = 3.0, exec_timeout_s: float = 80.0, ttl_s: float = 600.0, clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
        self.accept_timeout_s = accept_timeout_s  # seconds
        self.exec_timeout_s = exec_timeout_s # seconds
        self.ttl_s = ttl_s # seconds
        self._by_command_id: dict[str, CommandRecord] = {}
        self._clock = clock
        
    def now_utc(self) -> datetime:
        return self._clock()
    
    def get_record(self, command_id: str) -> CommandRecord | None:
        return self._by_command_id.get(command_id) 

    def on_received(self, cmd: Command) -> Transition:
        if cmd.command_id in self._by_command_id:
            return Transition(record = self._by_command_id[cmd.command_id], result= TransitionResult.DUPLICATE, changed= False)
        else:
            record = CommandRecord(command= cmd, status= CommandStatus.RECEIVED, received_at= self.now_utc())
            self._by_command_id[cmd.command_id] = record
            return Transition(record = record, result= TransitionResult.OK, changed= True)
    
    

    def on_accepted(self, command_id: str) -> Transition:
        record = self.get_record(command_id)
        if record is  None:
            return Transition(record=None, result=TransitionResult.UNKNOWN_COMMAND, changed= False)
        else:
            if record.status == CommandStatus.ACCEPTED:
                return Transition(record= record, result= TransitionResult.DUPLICATE, changed= False)
            elif record.is_terminal():
                return Transition(record= record, result= TransitionResult.TERMINAL, changed= False)
            elif record.status != CommandStatus.RECEIVED:
                return Transition(record= record, result= TransitionResult.INVALID_STATE, changed= False)
            else:
                record.status = CommandStatus.ACCEPTED
                record.accepted_at = self.now_utc()
                return Transition(record = record, result= TransitionResult.OK, changed= True)
        
    def on_executed(self, command_id: str) -> Transition:
        record = self.get_record(command_id)
        if record is None:
            return Transition(record=None, result= TransitionResult.UNKNOWN_COMMAND, changed= False)
        else:
            if record.status == CommandStatus.EXECUTED:
                return Transition( record= record, result= TransitionResult.DUPLICATE, changed= False)
            elif record.is_terminal():
                return Transition(record= record, result= TransitionResult.TERMINAL, changed= False)
            elif record.status != CommandStatus.ACCEPTED:
                return Transition(record= record, result= TransitionResult.INVALID_STATE, changed= False)
            else:
                record.status = CommandStatus.EXECUTED
                record.executed_at = self.now_utc()
                return Transition(record = record, result= TransitionResult.OK, changed= True)
        
    def on_rejected(self, command_id: str) -> Transition:
        record = self.get_record(command_id)
        if record is None:
            return Transition(record=None, result= TransitionResult.UNKNOWN_COMMAND, changed= False)
        else:
            if record.status == CommandStatus.REJECTED:
                return Transition(record= record, result= TransitionResult.DUPLICATE, changed= False)
            elif record.is_terminal():
                return Transition(record= record, result= TransitionResult.TERMINAL, changed= False)
            elif record.status != CommandStatus.RECEIVED:
                return Transition(record= record, result= TransitionResult.INVALID_STATE, changed= False)
            else:
                record.status = CommandStatus.REJECTED
                record.rejected_at = self.now_utc()
                return Transition(record= record, result= TransitionResult.OK, changed=True)

    def on_failed(self, command_id: str) -> Transition:
        record = self.get_record(command_id)
        if record is None:
            return Transition(record=None, result= TransitionResult.UNKNOWN_COMMAND, changed= False)
        else:
            if record.status == CommandStatus.FAILED:
                return Transition(record= record, result= TransitionResult.DUPLICATE, changed= False)
            elif record.is_terminal():
                return Transition(record= record, result= TransitionResult.TERMINAL, changed= False)
            elif record.status != CommandStatus.ACCEPTED:
                return Transition(record= record, result= TransitionResult.INVALID_STATE, changed= False)
            else:
                record.status = CommandStatus.FAILED
                record.failed_at = self.now_utc()
                return Transition(record= record, result= TransitionResult.OK, changed=True)

    def expire_timeouts(self) -> int:
        now = self.now_utc()
        expired = 0
        for record in self._by_command_id.values():
            if record.is_terminal(): continue
            if record.status == CommandStatus.RECEIVED:
                if (now - record.received_at).total_seconds() >= self.accept_timeout_s:
                    record.status = CommandStatus.TIMEOUT
                    record.timeout_at = now
                    expired += 1
            elif record.status == CommandStatus.ACCEPTED :
                if record.accepted_at is None: continue
                if (now - record.accepted_at).total_seconds() >= self.exec_timeout_s:
                    record.status = CommandStatus.TIMEOUT
                    record.timeout_at = now
                    expired += 1
        return expired
    
    def gc_ttl(self) -> int:
        now = self.now_utc()
        to_delete = []
        for command_id, record in self._by_command_id.items():
            if (now - record.received_at).total_seconds() >= self.ttl_s:
                to_delete.append(command_id)
        
        for cmd_id in to_delete: del self._by_command_id[cmd_id]
        return len(to_delete)