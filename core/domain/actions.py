"""
Domain actions for the trading system.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class TradeAction:
    """Represents a trading action decided by a strategy."""
    action_type: str
    instrument_token: int
    quantity: int
    price: Optional[float] = None
    metadata: Optional[dict] = None