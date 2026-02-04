from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class AckSnapshot:
    trigger: int
    command: str
    error: int
    message: str
    token: str
    mission_id: int