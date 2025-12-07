"""
IV Percentile volatility model implementation.
"""
from typing import Optional

from core.domain.state import MarketState
from core.domain.signals import VolSignal
from core.ports.vol_model import VolatilityModel


class IVPercentileModel(VolatilityModel):
    """
    Placeholder until IV feed is added.
    Emits nothing for now.
    Later, compute IV percentile from historical IV distribution.
    """

    name = "iv_percentile_model"

    def __init__(self, instrument_token: int):
        self.instrument_token = instrument_token

    def update(self, state: MarketState) -> Optional[VolSignal]:
        """Compute IV percentile based vol signal (placeholder)."""
        # later this will compute:
        # percentile = rank(current_iv)
        # thresholds → VOL_UP / VOL_DOWN
        return None