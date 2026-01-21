from datetime import datetime, timezone, timedelta
from hubcontroller.domain.commands import Command, CommandStatus
from hubcontroller.domain.registry import CommandRegistry, TransitionResult

def make_command(command_id: str) -> Command:
    return Command(
        command_id= command_id,
        command_type="test",
        payload= {'x':'s'}
        )

def test_duplicate_on_received():

    registry = CommandRegistry()
    cmd = make_command("cmd1")

    t1 = registry.on_received(cmd)
    assert t1.result == TransitionResult.OK
    assert t1.record.status == CommandStatus.RECEIVED
    assert t1.changed is True

    t2 = registry.on_received(cmd)
    assert t2.result == TransitionResult.DUPLICATE
    assert t2.record.status == CommandStatus.RECEIVED
    assert t2.changed is False

def test_happy_path_received_accepted_executed():
    registry = CommandRegistry()
    cmd = make_command("cmd1")
    t1 = registry.on_received(cmd)

    assert t1.result == TransitionResult.OK
    assert t1.record.status == CommandStatus.RECEIVED
    assert t1.changed is True
    assert t1.record.received_at is not None

    t2 = registry.on_accepted(cmd.command_id)
    assert t2.result == TransitionResult.OK
    assert t2.record.status == CommandStatus.ACCEPTED
    assert t2.changed is True
    assert t2.record.accepted_at is not None

    t3 = registry.on_executed(cmd.command_id)
    assert t3.result == TransitionResult.OK
    assert t3.record.status == CommandStatus.EXECUTED
    assert t3.changed is True
    assert t3.record.executed_at is not None