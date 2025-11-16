from abc import ABC, abstractmethod
from typing import Optional
from core.domain.state import MarketState
from core.domain.signals import VolSignal

class VolatilityModel(ABC):

    name: str = "base_vol_model"
    instrument_token: Optional[int] = None

    @abstractmethod
    def update(self, state: MarketState) -> Optional[VolSignal]:
        """Return a volatility signal, or None."""
        ...