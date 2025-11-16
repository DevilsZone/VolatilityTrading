from abc import ABC, abstractmethod
from typing import Iterable, List
from core.domain.types import Tick

class MarketDataFeed(ABC):

    @abstractmethod
    def subscribe(self, instruments: List[int]) -> None:
        ...

    @abstractmethod
    def stream(self) -> Iterable[Tick]:
        """
        LIVE mode → yields ticks in realtime
        BACKTEST → yields historical ticks/candles
        """
        ...