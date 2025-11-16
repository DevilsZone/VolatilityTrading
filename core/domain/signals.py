# core/domain/signals.py

from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class VolSignal:
    instrument_token: int
    kind: str
    strength: float
    timestamp: datetime