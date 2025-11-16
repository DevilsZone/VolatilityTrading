# infra/backtest/backtest_feed.py

from typing import Dict, List
from core.ports.market_data import MarketDataFeed
from core.domain.types import Tick, Candle


class BacktestFeed(MarketDataFeed):

    def __init__(self, candles_by_token: Dict[int, List[Candle]]):
        self.candles_by_token = candles_by_token

    def subscribe(self, instruments):
        pass

    def stream(self):
        """
        Replays candles in chronological order.
        Each candle is converted to 4 synthetic ticks.
        """

        # flatten all candles across tokens
        all_events = []

        for token, candles in self.candles_by_token.items():
            for c in candles:
                all_events.append(
                    Tick(token, c.timestamp, c.open, c.volume, c.oi)
                )
                all_events.append(
                    Tick(token, c.timestamp, c.high, c.volume, c.oi)
                )
                all_events.append(
                    Tick(token, c.timestamp, c.low, c.volume, c.oi)
                )
                all_events.append(
                    Tick(token, c.timestamp, c.close, c.volume, c.oi)
                )

        # sort by timestamp
        all_events.sort(key=lambda t: t.timestamp)

        for tick in all_events:
            yield tick
            # optional slow down:
            # time.sleep(0.001)