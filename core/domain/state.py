"""
Domain state for the trading system.
"""
from dataclasses import dataclass
from typing import Dict, List
from core.domain.types import Tick, Candle

@dataclass
class MarketState:
    """Represents the aggregate market state."""
    last_ticks: Dict[int, Tick]
    recent_candles: Dict[int, List[Candle]]
    positions: Dict[int, int]
    timestamp: float