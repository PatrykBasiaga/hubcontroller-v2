from hubcontroller.domain.commands import Command, CommandStatus
from hubcontroller.domain.registry import CommandRegistry, Transition, TransitionResult
from hubcontroller.domain.hub_state_provider import HubStateProvider
from hubcontroller.adapters.plc.commands import PlcSendStatus
from hubcontroller.adapters.plc.client import PlcClient
from guard import Guard
from typing import Callable
import time


class CommandProcessor:
    def __init__(self, command_registry: CommandRegistry, handlers: dict[str, Callable[[Command], None]], state_provider: HubStateProvider, guard: Guard, plc_client: PlcClient):
        self._command_registry = command_registry
        self._handlers = handlers
        self._state_provider = state_provider
        self._guard = guard
        self._plc_client = plc_client

    def should_dispatch(self, t: Transition) -> bool:
        if t.record is None:
            return False
            int(control_frame_dict["command_ids"])

        if t.result != TransitionResult.DUPLICATE:
            return True
        return t.record.status == CommandStatus.RECEIVED

    def _reject_command(self, command: Command) -> TransitionResult:
        t = self._command_registry.on_rejected(command.command_id)
        return t.result
    
    def _dispatch_command_to_plc_retry(self, command: Command) -> PlcSendStatus:
        
        last_status = PlcSendStatus.ERROR
        for attempt in range(3):
            if attempt > 0:
                time.sleep(0.1*(2**(attempt-1)))
            last_status = self._plc_client.plc_write_command(command)
            if last_status == PlcSendStatus.OK: 
                return last_status
            if last_status == PlcSendStatus.INVALID_PARAMETERS: 
                return last_status   
        return last_status

    def on_command(self, command: Command) -> TransitionResult | None:
        state = self._state_provider.get_snapshot()
        t = self._command_registry.on_received(command)

        if not self.should_dispatch(t):
            return t.result

        if command.command_type not in self._handlers:
            return self._reject_command(command)

        decision = self._guard.check(command, state)
        if decision.allowed is False:
            return self._reject_command(command)

        plc_send_status = self._dispatch_command_to_plc_retry(command)
        if plc_send_status == PlcSendStatus.OK:
            self._command_registry.on_dispatched(command.command_id)
            return None
        elif plc_send_status == PlcSendStatus.INVALID_PARAMETERS:
            return self._reject_command(command)
        else: 
            return None