# infra/backtest/backtest_runner.py

from datetime import datetime

from core.domain.types import Candle
from infra.backtest.historical_provider import ZerodhaHistoricalProvider
from infra.backtest.backtest_feed import BacktestFeed
from infra.backtest.simulated_broker import SimulatedBroker
from core.engine.runner import Engine


class BacktestRunner:

    def __init__(self, api_key, access_token):
        self.provider = ZerodhaHistoricalProvider(api_key, access_token)

    def run(
        self,
        instrument_tokens,
        start: datetime,
        end: datetime,
        interval,
        vol_models,
        strategies,
        risk_mgr
    ):

        # 1. Fetch candles for all tokens
        candles_by_token = {}

        for token in instrument_tokens:
            raw_candles = self.provider.get_candles(token, start, end, interval)

            candles = []
            for c in raw_candles:
                candles.append(
                    Candle(
                        instrument_token=token,
                        timestamp=c["date"],
                        open=c["open"],
                        high=c["high"],
                        low=c["low"],
                        close=c["close"],
                        volume=c["volume"],
                        oi=c.get("oi")
                    )
                )

            candles_by_token[token] = candles

        # 2. Initialise feed & broker
        feed = BacktestFeed(candles_by_token)
        broker = SimulatedBroker()

        # 3. Create engine & run
        engine = Engine(
            feed=feed,
            broker=broker,
            vol_models=vol_models,
            strategies=strategies,
            risk_mgr=risk_mgr
        )

        engine.run()