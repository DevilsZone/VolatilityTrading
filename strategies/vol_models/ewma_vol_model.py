from datetime import datetime
from math import log, sqrt
from typing import Optional

from core.ports.vol_model import VolatilityModel
from core.domain.state import MarketState
from core.domain.signals import VolSignal


class EWMAVolModel(VolatilityModel):
    """
    Exponentially Weighted Moving Average (EWMA) Volatility Model.
    Recursive formula:
      Variance_t = lambda * Variance_{t-1} + (1 - lambda) * Return_t^2
    """

    name = "ewma_vol_model"

    def __init__(
        self,
        instrument_token: int,
        decay_factor: float = 0.94,
        high_threshold: float = 0.015,
        low_threshold: float = 0.005,
        annualize_factor: float = 1.0,  # e.g. sqrt(252) for daily, or sqrt(252*375) for minutes
    ):
        self.instrument_token = instrument_token
        self.decay_factor = decay_factor
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.annualize_factor = annualize_factor

        self.last_price: Optional[float] = None
        self.current_variance: float = 0.0
        self.initialized = False

    def update(self, state: MarketState) -> Optional[VolSignal]:
        tick = state.last_ticks.get(self.instrument_token)
        if not tick or tick.last_price is None or tick.last_price <= 0:
            return None

        price = tick.last_price

        if self.last_price is None:
            self.last_price = price
            return None

        # Calculate log return
        ret = log(price / self.last_price)
        self.last_price = price

        # Update variance
        if not self.initialized:
            # Seed with squared return (instantly noisy, but settles quickly)
            self.current_variance = ret ** 2
            self.initialized = True
        else:
            self.current_variance = (
                self.decay_factor * self.current_variance
                + (1 - self.decay_factor) * (ret ** 2)
            )

        vol = sqrt(self.current_variance) * self.annualize_factor

        kind: Optional[str] = None
        if vol >= self.high_threshold:
            kind = "VOL_UP"
        elif vol <= self.low_threshold:
            kind = "VOL_DOWN"

        if not kind:
            return None

        denominator = (self.high_threshold - self.low_threshold) or 1.0
        strength = (vol - self.low_threshold) / denominator
        strength = max(0.0, min(1.0, strength))

        return VolSignal(
            instrument_token=self.instrument_token,
            kind=kind,
            strength=strength,
            timestamp=tick.timestamp if isinstance(tick.timestamp, datetime) else datetime.now(),
        )
