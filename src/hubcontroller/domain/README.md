# Stage 1: Command + CommandRegistry (State Machine)

This stage introduces a deterministic **domain core** for command handling:
- command registration by `command_id`
- explicit state transitions (ACK / EXEC / REJECT / FAIL)
- idempotency (duplicate events cause no side effects)
- strict out-of-order handling (no “auto-fixing” invalid sequences)
- foundation for timeouts, TTL cleanup, and the future `CommandProcessor`

---

## 1) Domain model

### `Command`
- immutable (`frozen` dataclass)
- identification: `command_id`
- type: `command_type`
- payload: `payload` (`Mapping`)

### `CommandStatus`
Available statuses:
- `RECEIVED`
- `ACCEPTED`
- `EXECUTED`
- `REJECTED`
- `FAILED`
- `TIMEOUT`

---

## 2) State machine (allowed transitions)

Allowed transitions:

- `RECEIVED  -> ACCEPTED`
- `ACCEPTED  -> EXECUTED`
- `RECEIVED  -> REJECTED`
- `ACCEPTED  -> FAILED`
- `RECEIVED  -> TIMEOUT` (when `accept_timeout_s` expires)
- `ACCEPTED  -> TIMEOUT` (when `exec_timeout_s` expires)

### Terminal states
Once a terminal state is reached, **no further state changes are allowed**:

- `EXECUTED`
- `REJECTED`
- `FAILED`
- `TIMEOUT`

---

## 3) Idempotency and out-of-order handling

### Idempotency (duplicates)
If an event targets a command that is **already in the target state**, it is treated as a duplicate:
- second `ACCEPTED` for an already `ACCEPTED` command → `DUPLICATE`
- second `EXECUTED` for an already `EXECUTED` command → `DUPLICATE`
- second `RECEIVED` for an existing `command_id` → `DUPLICATE`

Duplicate events **must not modify state** and **must not trigger side effects**.

### Out-of-order events
Out-of-order events are handled strictly and are **not auto-corrected**:
- `EXECUTED` before `ACCEPTED` → `INVALID_STATE`
- `ACCEPTED` after `EXECUTED` → `TERMINAL`

This allows proper observability (metrics/logs) and keeps ordering logic out of the domain core.

---

## 4) Transition API contract

Every `CommandRegistry` method returns a unified `Transition` object:

- `record: CommandRecord | None`
- `result: TransitionResult`
- `changed: bool`

### `TransitionResult`
Possible results:
- `OK` – transition applied successfully (state changed)
- `DUPLICATE` – duplicate event for the current state
- `UNKNOWN_COMMAND` – no record exists for the given `command_id`
- `INVALID_STATE` – event does not match the current state
- `TERMINAL` – command is already in a terminal state

---

## 5) Stage 1 scope (implementation order)

1. State machine definition (this document)
2. Unified transition results (`TransitionResult` + `Transition`)
3. Idempotency and out-of-order rules
4. Additional events: `on_rejected`, `on_failed`
5. Timeouts as a tick-based operation: `expire_timeouts()`
6. Cleanup via TTL: `gc_ttl()`
7. Injectable clock (`clock`) for testability (no `sleep()`)

---

## 6) Minimal required tests

- duplicate `on_received` → `DUPLICATE`
- happy path: `RECEIVED → ACCEPTED → EXECUTED`
- invalid order: `RECEIVED → EXECUTED` → `INVALID_STATE`
- accept timeout: after `accept_timeout_s`, state becomes `TIMEOUT` (using a fake clock)

> Rule: timeout tests must not use `sleep()` — only a controlled, injected clock.
