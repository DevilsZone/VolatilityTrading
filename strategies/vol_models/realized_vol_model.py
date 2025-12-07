"""
Realized volatility model implementation.
"""
# strategies/vol_models/realized_vol_model.py

from collections import deque
from datetime import datetime
from math import log, sqrt
from typing import Deque, Optional

from core.ports.vol_model import VolatilityModel
from core.domain.state import MarketState
from core.domain.signals import VolSignal


class RealizedVolModel(VolatilityModel):
    """
    Rolling realized volatility (std dev of log returns) for ONE instrument.

    - Maintains a rolling window of prices
    - Computes log returns and std dev
    - Compares against high/low thresholds
    - Emits VOL_UP / VOL_DOWN signals
    """

    name = "realized_vol_model"

    def __init__(
        self,
        instrument_token: int,
        lookback: int = 30,
        high_threshold: float = 0.01,
        low_threshold: float = 0.003,
        annualize_factor: float = 1.0,
    ):
        """
        :param instrument_token: this instrument this model watches (e.g., NIFTY index token)
        :param lookback: the number of returns in rolling window
        :param high_threshold: vol above this ⇒ VOL_UP
        :param low_threshold: vol below this ⇒ VOL_DOWN
        :param annualize_factor: multiply std by this if you want annualized vol
        """
        self.instrument_token = instrument_token
        self.lookback = lookback
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.annualize_factor = annualize_factor

        # store lookback+1 prices to compute `lookback` returns
        self._prices: Deque[float] = deque(maxlen=lookback + 1)

    def update(self, state: MarketState) -> Optional[VolSignal]:
        """Compute realized vol from recent prices."""
        tick = state.last_ticks.get(self.instrument_token)
        if tick is None:
            return None

        price = tick.last_price
        if price is None or price <= 0:
            return None

        self._prices.append(price)

        # wait until we have enough data
        if len(self._prices) < self.lookback + 1:
            return None

        # compute log returns
        prices = list(self._prices)
        rets = []
        for i in range(1, len(prices)):
            r = log(prices[i] / prices[i - 1])
            rets.append(r)

        n = len(rets)
        if n < 2:
            return None

        mean_r = sum(rets) / n
        var = sum((r - mean_r) ** 2 for r in rets) / (n - 1)
        vol = sqrt(var) * self.annualize_factor

        kind: Optional[str] = None
        if vol >= self.high_threshold:
            kind = "VOL_UP"
        elif vol <= self.low_threshold:
            kind = "VOL_DOWN"

        if not kind:
            return None

        # Map vol to [0,1] strengths (roughly)
        denominator = (self.high_threshold - self.low_threshold) or 1.0
        strength = (vol - self.low_threshold) / denominator
        strength = max(0.0, min(1.0, strength))

        return VolSignal(
            instrument_token=self.instrument_token,
            kind=kind,
            strength=strength,
            timestamp=tick.timestamp if isinstance(tick.timestamp, datetime) else datetime.now(),
        )