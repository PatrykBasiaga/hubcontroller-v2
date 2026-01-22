from datetime import datetime, timezone, timedelta
from hubcontroller.domain.commands import Command, CommandStatus
from hubcontroller.domain.registry import CommandRegistry, TransitionResult

def make_command(command_id: str) -> Command:
    return Command(
        command_id= command_id,
        command_type="test",
        payload= {'x':'s'}
        )

def test_received_then_accepted():
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

def test_negative_path_duplicate_on_received():

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

def test_invalid_order_received_then_executed():
    registry = CommandRegistry()
    cmd = make_command("cmd1")
    t1 = registry.on_received(cmd)

    assert t1.result == TransitionResult.OK
    assert t1.record.status == CommandStatus.RECEIVED
    assert t1.changed is True
    assert t1.record.received_at is not None

    t2 = registry.on_executed(cmd.command_id)
    assert t2 is not None
    assert t2.result == TransitionResult.INVALID_STATE
    assert t2.record.status == CommandStatus.RECEIVED
    assert t2.changed is False
    assert t2.record.executed_at is None

def test_terminal_state_block_further_transitions():
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

    accepted_at_t3 = t3.record.accepted_at
    executed_at_t3 = t3.record.executed_at

    t4 = registry.on_accepted(cmd.command_id)
    assert t4.result == TransitionResult.TERMINAL
    assert t4.record.status == CommandStatus.EXECUTED
    assert t4.changed is False
    assert t4.record.accepted_at is not None
    assert t4.record.executed_at is not None
    assert t4.record.accepted_at == accepted_at_t3
    assert t4.record.executed_at == executed_at_t3

def test_terminal_state_duplication():
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

    accepted_at_t3 = t3.record.accepted_at
    executed_at_t3 = t3.record.executed_at

    t4 = registry.on_executed(cmd.command_id)
    assert t4 is not None
    assert t4.result == TransitionResult.DUPLICATE
    assert t4.record.status == CommandStatus.EXECUTED
    assert t4.changed is False
    assert t4.record.accepted_at is not None
    assert t4.record.executed_at is not None
    assert t4.record.accepted_at == accepted_at_t3
    assert t4.record.executed_at == executed_at_t3

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

    # RECEIVED
    t1 = registry.on_received(cmd)
    assert t1.result == TransitionResult.OK
    assert t1.record.status == CommandStatus.RECEIVED
    assert t1.changed is True
    assert t1.record.received_at is not None

    fake_clock.advance(3.1)
    expired = registry.expire_timeouts()
    assert expired == 1

    rec = registry.get_record("cmd1")
    
    assert rec is not None
    assert rec.status == CommandStatus.TIMEOUT
    assert rec.timeout_at == fake_clock.now()

def test_terminal_command_timeout():
    fake_clock = FakeClock(datetime.now(timezone.utc))
    registry = CommandRegistry(clock= fake_clock.now, exec_timeout_s=10.0)
    cmd = make_command("cmd1")

    t1 = registry.on_received(cmd)
    assert t1.record.status == CommandStatus.RECEIVED

    t2 = registry.on_accepted(cmd.command_id)
    assert t2.record.status == CommandStatus.ACCEPTED

    t3 = registry.on_executed(cmd.command_id)
    assert t3.record.status == CommandStatus.EXECUTED
    executed_at_before_timeout = t3.record.executed_at

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

    t1 = registry.on_received(cmd)
    assert t1.record is not None
    assert t1.record.status == CommandStatus.RECEIVED
    rec_before_ttl = registry.get_record("cmd1")

    deleted_before_ttl = registry.gc_ttl()
    assert deleted_before_ttl == 0
    registry.get_record("cmd1") == rec_before_ttl
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