# HubController — Stage 1  
## Domain Core: założenia, reguły i dobre praktyki

> **Cel dokumentu**  
> Ten plik opisuje **jak działa Stage 1**,  
> **dlaczego kod jest napisany w taki sposób**,  
> oraz **jakie dobre praktyki są tu świadomie stosowane**.  
>
> Czytaj **codziennie przed rozpoczęciem pracy**, żeby utrzymać właściwy mindset.

---

## 🎯 Cel Stage 1

Zbudować **deterministyczny, testowalny domain core** do obsługi komend:

- rejestracja komend po `command_id`
- jawna maszyna stanów (state machine)
- idempotencja (duplikaty bez side-effectów)
- ścisła obsługa kolejności (out-of-order ≠ auto-fix)
- tick-based timeouty (bez `sleep`)
- TTL cleanup (kontrola pamięci)
- fundament pod `CommandProcessor` (Stage 2)

---

## 🧱 Model domeny

### `Command` (immutable)

- `@dataclass(frozen=True)`
- pola:
  - `command_id`
  - `command_type`
  - `payload`

**Dlaczego:**
- brak mutacji = deterministyka
- łatwiejsze testy
- brak „zmian w locie”
- payload nie może się rozjechać między eventami

---

### `CommandStatus` (Enum)

Dostępne stany:

- `RECEIVED`
- `ACCEPTED`
- `EXECUTED`
- `REJECTED`
- `FAILED`
- `TIMEOUT`

---

### `CommandRecord`

Przechowuje:
- aktualny `status`
- timestampy:
  - `received_at`
  - `accepted_at`
  - `executed_at`
  - `rejected_at`
  - `failed_at`
  - `timeout_at`

```text
CommandRecord = aktualny stan + pełna historia czasu

