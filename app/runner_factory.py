# app/runner_factory.py

from datetime import datetime

from infra.dummy.dummy_feed import DummyFeed
from infra.dummy.dummy_broker import DummyBroker
from infra.dummy.dummy_strategy import DummyStrategy
from infra.dummy.dummy_risk import DummyRiskManager

from infra.backtest.backtest_feed import BacktestFeed
from infra.backtest.simulated_broker import SimulatedBroker
from infra.backtest.historical_provider import ZerodhaHistoricalProvider

from core.engine.runner import Engine
from core.domain.types import Candle
from strategies.option_strategies.high_vol_long_straddle import HighVolLongStraddleStrategy
from strategies.option_strategies.long_vol_short_condor import LowVolShortCondorStrategy

# NEW
from strategies.vol_models.realized_vol_model import RealizedVolModel
from infra.zerodtha.zerodtha_broker import ZerodhaBroker
from infra.zerodtha.zerodtha_feed import ZerodhaFeed


class RunnerFactory:

    @staticmethod
    def build(config):
        mode = config.mode

        if mode == "dummy":
            return RunnerFactory._build_dummy(config)
        elif mode == "backtest":
            return RunnerFactory._build_backtest(config)
        elif mode == "live":
            return RunnerFactory._build_live(config)
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    @staticmethod
    def _build_dummy(config):
        feed = DummyFeed(config.instruments)
        broker = DummyBroker()

        # you can keep the dummy here or also use RealizedVolModel if you want
        vol_models = [
            RealizedVolModel(instrument_token=token, lookback=30)
            for token in config.instruments
        ]
        strategies = [DummyStrategy()]
        risk_mgr = DummyRiskManager()

        return Engine(feed, broker, vol_models, strategies, risk_mgr)

    @staticmethod
    def _build_backtest(config):
        provider = ZerodhaHistoricalProvider(config.api_key, config.access_token)

        candles_by_token = {}
        for token in config.instruments:
            raw = provider.get_candles(
                token,
                datetime.fromisoformat(config.backtest_start),
                datetime.fromisoformat(config.backtest_end),
                config.backtest_interval,
            )

            candles = [
                Candle(
                    instrument_token=token,
                    timestamp=c["date"],
                    open=c["open"],
                    high=c["high"],
                    low=c["low"],
                    close=c["close"],
                    volume=c["volume"],
                    oi=c.get("oi"),
                )
                for c in raw
            ]
            candles_by_token[token] = candles

        feed = BacktestFeed(candles_by_token)
        broker = SimulatedBroker()

        # Vol model: realized vol per instrument
        vol_models = [
            RealizedVolModel(
                instrument_token=token,
                lookback=30,
                high_threshold=0.01,
                low_threshold=0.003,
            )
            for token in config.instruments
        ]

        # Strategies: one long-straddle + one condor per instrument
        strategies = []
        for token in config.instruments:
            strategies.append(HighVolLongStraddleStrategy(underlying_token=token))
            strategies.append(LowVolShortCondorStrategy(underlying_token=token))

        risk_mgr = DummyRiskManager()  # or you're real one

        return Engine(
            feed=feed,
            broker=broker,
            vol_models=vol_models,
            strategies=strategies,
            risk_mgr=risk_mgr,
            state_repo=None,
        )

    @staticmethod
    def _build_live(config):
        # 1. Init Broker & Feed
        broker = ZerodhaBroker(config.api_key, config.access_token)
        feed = ZerodhaFeed(config.api_key, config.access_token)
        
        feed.subscribe(config.instruments)

        from strategies.vol_models.ewma_vol_model import EWMAVolModel
        from strategies.vol_models.garch_vol_model import GARCHVolModel

        # 2. Vol Models (Live)
        vol_models = []
        for token in config.instruments:
            # Realized Vol (Rolling Window)
            vol_models.append(RealizedVolModel(
                instrument_token=token,
                lookback=30,
                high_threshold=0.01,
                low_threshold=0.003
            ))
            # EWMA
            vol_models.append(EWMAVolModel(
                instrument_token=token,
                decay_factor=0.94
            ))
            # GARCH
            vol_models.append(GARCHVolModel(
                instrument_token=token
            ))

        # 3. Strategies
        strategies = []
        for token in config.instruments:
            strategies.append(HighVolLongStraddleStrategy(underlying_token=token))
            strategies.append(LowVolShortCondorStrategy(underlying_token=token))

        # 4. Risk Manager (Use Dummy for now, or a real one if available)
        risk_mgr = DummyRiskManager()

        return Engine(
            feed=feed,
            broker=broker,
            vol_models=vol_models,
            strategies=strategies,
            risk_mgr=risk_mgr,
        )