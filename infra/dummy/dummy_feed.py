# infra/dummy/dummy_feed.py

import time
from datetime import datetime
from core.ports.market_data import MarketDataFeed
from core.domain.types import Tick


class DummyFeed(MarketDataFeed):

    def __init__(self, instrument_tokens):
        self.tokens = instrument_tokens
        self.counter = 0

    def subscribe(self, instruments):
        pass  # not needed in dummy

    def stream(self):
        """
        Yields synthetic ticks that increase in price over time.
        """
        while True:
            for token in self.tokens:
                tick = Tick(
                    instrument_token=token,
                    timestamp=datetime.now(),
                    last_price=100 + self.counter,
                    volume=1000 + self.counter,
                    oi=None
                )
                yield tick

            self.counter += 1
            time.sleep(1)  # slow it down for readability