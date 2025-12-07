"""
Domain ports for market data feeds.
"""
from abc import ABC, abstractmethod
from typing import Iterable, List
from core.domain.types import Tick

class MarketDataFeed(ABC):
    """Abstract base class for market data feeds."""

    @abstractmethod
    def subscribe(self, instruments: List[int]) -> None:
        """Subscribe to a list of instruments."""

    @abstractmethod
    def stream(self) -> Iterable[Tick]:
        """
        LIVE mode → yields ticks in realtime
        BACKTEST → yields historical ticks/candles
        """