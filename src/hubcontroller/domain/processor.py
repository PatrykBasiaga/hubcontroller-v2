from hubcontroller.domain.commands import Command
from hubcontroller.domain.registry import CommandRegistry
from typing import Callable, Any


class CommandProcessor:
    def __init__(self, command_registry: CommandRegistry, handlers: dict[str, Callable[[Command], None]], state_provider: Any, guard: Any):
        self._command_registry = command_registry
        self._handlers = handlers
        self._state_provider = state_provider
        self._guard = guard

    
    def on_command(self, command: Command) -> None:
        return None