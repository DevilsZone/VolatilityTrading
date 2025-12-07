"""
Composite volatility model (aggregation).
"""
# strategies/vol_models/composite_vol_model.py

from typing import Optional, Iterable
from datetime import datetime

from core.domain.state import MarketState
from core.domain.signals import VolSignal
from core.ports.vol_model import VolatilityModel


class CompositeVolModel(VolatilityModel):
    """
    Combine several vol models using majority vote / weighted score.
    """

    name = "composite_vol_model"

    def __init__(self, models: Iterable[VolatilityModel]):
        self.models = list(models)
        # assume all child models refer to the same instrument
        self.instrument_token = (
            self.models[0].instrument_token if self.models else None
        )

    def update(self, state: MarketState) -> Optional[VolSignal]:
        """Aggregate signals from child models."""
        ups = []
        downs = []

        for m in self.models:
            sig = m.update(state)
            if sig is None:
                continue
            if sig.kind == "VOL_UP":
                ups.append(sig.strength)
            elif sig.kind == "VOL_DOWN":
                downs.append(sig.strength)

        if not ups and not downs:
            return None

        if len(ups) > len(downs):
            strength = sum(ups) / len(ups)
            token = self.instrument_token
            if token is None:
                return None
            return VolSignal(
                instrument_token=token,
                kind="VOL_UP",
                strength=strength,
                timestamp=datetime.now(),
            )

        if len(downs) > len(ups):
            strength = sum(downs) / len(downs)
            token = self.instrument_token
            if token is None:
                return None
            return VolSignal(
                instrument_token=token,
                kind="VOL_DOWN",
                strength=strength,
                timestamp=datetime.now(),
            )

        return None