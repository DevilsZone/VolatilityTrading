# infra/dummy/dummy_vol_model.py

from core.ports.vol_model import VolatilityModel
from core.domain.state import MarketState
from core.domain.signals import VolSignal
from datetime import datetime


class DummyVolModel(VolatilityModel):

    name = "dummy_vol_model"

    def __init__(self):
        self.counter = 0

    def update(self, state: MarketState):
        self.counter += 1
        if self.counter % 5 == 0:
            # simulate volatility rising
            any_token = list(state.last_ticks.keys())[0]
            return VolSignal(
                instrument_token=any_token,
                kind="VOL_UP",
                strength=0.8,
                timestamp=datetime.now()
            )
        return None