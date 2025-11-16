# strategies/vol_models/bollinger_vol_model.py

from collections import deque
from math import sqrt
from typing import Optional
from datetime import datetime

from core.ports.vol_model import VolatilityModel
from core.domain.state import MarketState
from core.domain.signals import VolSignal
from core.domain.types import Candle


class BollingerVolModel(VolatilityModel):
    """
    Bollinger Band Width as a volatility indicator.
    width = (upper - lower) / middle
    Uses recent candle CLOSE prices.
    """

    name = "bollinger_vol_model"

    def __init__(
        self,
        instrument_token: int,
        period: int = 20,
        high_threshold: float = 0.05,
        low_threshold: float = 0.02,
    ):
        self.instrument_token = instrument_token
        self.period = period
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self._closes = deque(maxlen=period)

    def update(self, state: MarketState) -> Optional[VolSignal]:
        candles = state.recent_candles.get(self.instrument_token)
        if not candles:
            return None

        # push the last close into a window
        last: Candle = candles[-1]
        if last.close is None:
            return None

        self._closes.append(last.close)

        if len(self._closes) < self.period:
            return None

        closes = list(self._closes)
        mean = sum(closes) / self.period
        var = sum((c - mean) ** 2 for c in closes) / self.period
        std = sqrt(var)

        upper = mean + 2 * std
        lower = mean - 2 * std
        bw = (upper - lower) / mean  # bandwidth (fraction)

        kind: Optional[str] = None
        if bw >= self.high_threshold:
            kind = "VOL_UP"
        elif bw <= self.low_threshold:
            kind = "VOL_DOWN"

        if not kind:
            return None

        denominator = (self.high_threshold - self.low_threshold) or 1.0
        strength = (bw - self.low_threshold) / denominator
        strength = max(0.0, min(1.0, strength))

        return VolSignal(
            instrument_token=self.instrument_token,
            kind=kind,
            strength=strength,
            timestamp=datetime.now(),
        )