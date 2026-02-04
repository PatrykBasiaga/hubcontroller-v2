from datetime import datetime, timezone, timedelta
from hubcontroller.domain.commands import Command, CommandStatus
from hubcontroller.domain.registry import CommandRegistry, TransitionResult, CommandRecord

def make_command(command_id: str) -> Command:
    return Command(
        command_id= command_id,
        command_type="test",
        payload= {'x':'s'}
        )

def given_command_is_received(registry: CommandRegistry, cmd: Command) -> CommandRecord:
    t = registry.on_received(cmd)
    assert t.record is not None
    assert t.result == TransitionResult.OK
    assert t.record.status == CommandStatus.RECEIVED
    assert t.changed is True
    assert t.record.received_at is not None
    return t.record

def given_command_is_accepted(registry: CommandRegistry, cmd: Command) -> CommandRecord:
    given_command_is_received(registry, cmd)
    t = registry.on_accepted(cmd.command_id)
    assert t.record is not None
    assert t.result == TransitionResult.OK
    assert t.record.status == CommandStatus.ACCEPTED
    assert t.changed is True
    assert t.record.accepted_at is not None
    return t.record

def given_command_is_executed(registry: CommandRegistry, cmd: Command) -> CommandRecord:
    given_command_is_accepted(registry, cmd)
    t = registry.on_executed(cmd.command_id)
    assert t.record is not None
    assert t.result == TransitionResult.OK
    assert t.record.status == CommandStatus.EXECUTED
    assert t.changed is True
    assert t.record.executed_at is not None
    return t.record


def test_negative_path_duplicate_on_received():

    registry = CommandRegistry()
    cmd = make_command("cmd1")
    given_command_is_received(registry, cmd)

    t2 = registry.on_received(cmd)
    assert t2.result == TransitionResult.DUPLICATE
    assert t2.record.status == CommandStatus.RECEIVED
    assert t2.changed is False

def test_happy_path_received_accepted_executed():
    registry = CommandRegistry()
    cmd = make_command("cmd1")
    given_command_is_executed(registry, cmd)

def test_invalid_order_received_then_executed():
    registry = CommandRegistry()
    cmd = make_command("cmd1")
    given_command_is_received(registry, cmd)

    t2 = registry.on_executed(cmd.command_id)
    assert t2 is not None
    assert t2.result == TransitionResult.INVALID_STATE
    assert t2.record.status == CommandStatus.RECEIVED
    assert t2.changed is False
    assert t2.record.executed_at is None

def test_terminal_state_block_further_transitions():
    registry = CommandRegistry()
    cmd = make_command("cmd1")
    given_command_is_received(registry, cmd)
    accepted = given_command_is_accepted(registry, cmd)
    executed = given_command_is_executed(registry, cmd)


    accepted_at = accepted.accepted_at
    executed_at = executed.executed_at

    t4 = registry.on_accepted(cmd.command_id)
    assert t4.result == TransitionResult.TERMINAL
    assert t4.record.status == CommandStatus.EXECUTED
    assert t4.changed is False
    assert t4.record.accepted_at is not None
    assert t4.record.executed_at is not None
    assert t4.record.accepted_at == accepted_at
    assert t4.record.executed_at == executed_at

def test_terminal_state_duplication():
    registry = CommandRegistry()
    cmd = make_command("cmd1")
    given_command_is_received(registry, cmd)
    accepted = given_command_is_accepted(registry, cmd)
    executed = given_command_is_executed(registry, cmd)

    accepted_at = accepted.accepted_at
    executed_at = executed.executed_at

    t4 = registry.on_executed(cmd.command_id)
    assert t4 is not None
    assert t4.result == TransitionResult.DUPLICATE
    assert t4.record.status == CommandStatus.EXECUTED
    assert t4.changed is False
    assert t4.record.accepted_at is not None
    assert t4.record.executed_at is not None
    assert t4.record.accepted_at == accepted_at
    assert t4.record.executed_at == executed_at

def test_unknown_command():
    registry = CommandRegistry()
    t1 = registry.on_accepted("cmd1")

    assert t1 is not None
    assert t1.result == TransitionResult.UNKNOWN_COMMAND
    assert t1.record is None
    assert t1.changed is False

def test_accept_timeout_expired():
    fake_clock = FakeClock(datetime.now(timezone.utc))
    registry = CommandRegistry(clock=fake_clock.now, accept_timeout_s=3.0)
    cmd = make_command("cmd1")
    record = given_command_is_received(registry, cmd)

    fake_clock.advance(3.1)
    expired = registry.expire_timeouts()
    assert expired == 1
    assert record is not None
    assert record.status == CommandStatus.TIMEOUT
    assert record.timeout_at == fake_clock.now()

def test_terminal_command_timeout():
    fake_clock = FakeClock(datetime.now(timezone.utc))
    registry = CommandRegistry(clock= fake_clock.now, exec_timeout_s=10.0)
    cmd = make_command("cmd1")

    given_command_is_received(registry, cmd)
    given_command_is_accepted(registry, cmd)
    executed = given_command_is_executed(registry, cmd)

    executed_at_before_timeout = executed.executed_at

    fake_clock.advance(11.0)
    expired = registry.expire_timeouts()
    assert expired == 0

    rec = registry.get_record("cmd1")
    assert rec is not None
    assert rec.status == CommandStatus.EXECUTED
    assert rec.executed_at is not None
    assert rec.timeout_at is None
    assert rec.executed_at == executed_at_before_timeout

def test_ttl_command_deletion():
    fake_clock = FakeClock(datetime.now(timezone.utc))
    registry = CommandRegistry(clock=fake_clock.now, ttl_s=10.0)
    cmd = make_command("cmd1")

    given_command_is_received(registry, cmd)
    rec_before_ttl = registry.get_record("cmd1")

    deleted_before_ttl = registry.gc_ttl()
    assert deleted_before_ttl == 0
    assert registry.get_record("cmd1") is rec_before_ttl
    assert registry.get_record("cmd1") is not None

    fake_clock.advance(10.0)
    deleted = registry.gc_ttl()
    assert deleted == 1
    assert registry.get_record("cmd1") is None


class FakeClock:
    def __init__(self, start: datetime):
        self._t = start

    def now(self) -> datetime:
        return self._t

    def advance(self, second: float) -> None:
        self._t = self._t + timedelta(seconds=second)
