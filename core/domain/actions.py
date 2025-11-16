from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class TradeAction:
    action_type: str
    instrument_token: int
    quantity: int
    price: Optional[float] = None
    metadata: Optional[dict] = None