from adapters.plc.protocol.models.exec_snapshot import ExecSnapshot
from datetime import datetime, timezone
from typing import Callable

class ExecRegistry:
    def __init__(self, ttl_s: float = 600.0, clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
        self._execs: dict[str, tuple[str, datetime]] = {}
        self._ttl_s = ttl_s
        self._clock = clock
    
    def now_utc(self) -> datetime:
        return self._clock()
    
    def is_duplicate(self, snapshot: ExecSnapshot) -> bool:
        return snapshot.token in self._execs
        
    def store_exec(self, snapshot: ExecSnapshot) -> None:
        now = self.now_utc()
        self._execs[snapshot.token] = (snapshot.command, now)

    def gc_ttl(self) -> None:
        now = self.now_utc()
        to_delete = []
        for token, (_, sent_at) in self._execs.items():
            if (now - sent_at).total_seconds() >= self._ttl_s:
                to_delete.append(token)
        for token in to_delete:
            del self._execs[token]
