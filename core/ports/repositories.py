from abc import ABC, abstractmethod
from typing import List
from core.domain.types import Candle

class MarketStateRepository(ABC):

    @abstractmethod
    def store_candles(self, instrument_token: int, candles: List[Candle]) -> None:
        ...

    @abstractmethod
    def load_candles(self, instrument_token: int) -> List[Candle]:
        ...