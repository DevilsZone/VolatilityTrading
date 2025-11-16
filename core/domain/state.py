from dataclasses import dataclass
from typing import Dict, List
from core.domain.types import Tick, Candle

@dataclass
class MarketState:
    last_ticks: Dict[int, Tick]
    recent_candles: Dict[int, List[Candle]]
    positions: Dict[int, int]
    timestamp: float