"""
GARCH (1,1) volatility model implementation.
"""
from datetime import datetime
from math import log, sqrt
from typing import Optional

from core.ports.vol_model import VolatilityModel
from core.domain.state import MarketState
from core.domain.signals import VolSignal


class GARCHVolModel(VolatilityModel):
    """
    Simplified GARCH(1,1) Volatility Model.
    Formula:
      Sigma_t^2 = omega + alpha * epsilon_{t-1}^2 + beta * Sigma_{t-1}^2
    where epsilon_{t-1} is the previous return (assuming the mean return is approx 0 for high freq).
    """

    name = "garch_vol_model"

    def __init__(
        self,
        instrument_token: int,
        omega: float = 0.000001,
        alpha: float = 0.1,
        beta: float = 0.85,
        high_threshold: float = 0.015,
        low_threshold: float = 0.005,
        annualize_factor: float = 1.0,
    ):
        self.instrument_token = instrument_token
        self.omega = omega
        self.alpha = alpha
        self.beta = beta
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.annualize_factor = annualize_factor

        self.last_price: Optional[float] = None
        self.current_variance: float = omega / (1 - alpha - beta)  # Long-run variance seed
        self.initialized = False

    def update(self, state: MarketState) -> Optional[VolSignal]:
        """Compute GARCH variance update."""
        tick = state.last_ticks.get(self.instrument_token)
        if not tick or tick.last_price is None or tick.last_price <= 0:
            return None

        price = tick.last_price

        if self.last_price is None:
            self.last_price = price
            return None

        # Log return
        ret = log(price / self.last_price)
        self.last_price = price

        # Update GARCH variance
        # sigma^2 = omega + alpha * r^2 + beta * sigma_prev^2
        # (Using return as proxy for residual epsilon)
        self.current_variance = (
            self.omega
            + self.alpha * (ret ** 2)
            + self.beta * self.current_variance
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
