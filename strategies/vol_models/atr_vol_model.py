# strategies/vol_models/atr_vol_model.py

from collections import deque
from typing import Optional
from datetime import datetime

from core.ports.vol_model import VolatilityModel
from core.domain.state import MarketState
from core.domain.signals import VolSignal
from core.domain.types import Candle


class ATRVolModel(VolatilityModel):
    """
    ATR volatility model based on recent candles (not ticks).
    ATR% = ATR / close
    Emits VOL_UP / VOL_DOWN based on thresholds.
    """

    name = "atr_vol_model"

    def __init__(
        self,
        instrument_token: int,
        period: int = 14,
        high_threshold: float = 0.012,
        low_threshold: float = 0.004,
    ):
        self.instrument_token = instrument_token
        self.period = period
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self._tr_values = deque(maxlen=period)

    def update(self, state: MarketState) -> Optional[VolSignal]:
        candles = state.recent_candles.get(self.instrument_token)
        if not candles or len(candles) < 2:
            return None

        # use last two candles
        prev: Candle = candles[-2]
        last: Candle = candles[-1]

        h = last.high
        l = last.low
        prev_close = prev.close
        close = last.close

        if h is None or l is None or prev_close is None or close is None:
            return None

        tr = max(
            h - l,
            abs(h - prev_close),
            abs(l - prev_close),
        )

        self._tr_values.append(tr)
        if len(self._tr_values) < self.period:
            return None

        atr = sum(self._tr_values) / len(self._tr_values)
        atr_pct = atr / close

        kind: Optional[str] = None
        if atr_pct >= self.high_threshold:
            kind = "VOL_UP"
        elif atr_pct <= self.low_threshold:
            kind = "VOL_DOWN"

        if not kind:
            return None

        denominator = (self.high_threshold - self.low_threshold) or 1.0
        strength = (atr_pct - self.low_threshold) / denominator
        strength = max(0.0, min(1.0, strength))

        return VolSignal(
            instrument_token=self.instrument_token,
            kind=kind,
            strength=strength,
            timestamp=datetime.now(),
        )