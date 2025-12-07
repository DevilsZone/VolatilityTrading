"""
The runner module orchestrates the entire trading loop.
"""
# core/engine/runner.py

from typing import List
from core.engine.event_loop import EventLoop
from core.ports.market_data import MarketDataFeed
from core.ports.broker import Broker
from core.ports.vol_model import VolatilityModel
from core.ports.strategy import Strategy, StrategyContext
from core.ports.risk import RiskManager
from core.domain.actions import TradeAction


class Engine:
    """
    The central orchestrator of the trading system.
    Handles:
      - reading ticks from feed
      - updating market state
      - calling vol models
      - executing strategies
      - applying risk management
    """

    def __init__(self,
                 feed: MarketDataFeed,
                 broker: Broker,
                 vol_models: List[VolatilityModel],
                 strategies: List[Strategy],
                 risk_mgr: RiskManager,
                 state_repo=None):
        self.feed = feed
        self.broker = broker
        self.vol_models = vol_models
        self.strategies = strategies
        self.risk_mgr = risk_mgr
        self.state_repo = state_repo

        self.loop = EventLoop()

    def run(self):
        """
        Main loop for the trading engine.
        NOTE: In Step 1, we ONLY print actions, not execute broker orders.
        """
        print("Engine started...")

        for tick in self.feed.stream():

            # ---- 1. Update internal market state ----
            state = self.loop.update_state_with_tick(tick)

            # ---- 2. Get current broker positions ----
            positions = {pos.instrument_token: pos.quantity
                         for pos in self.broker.get_positions()}
            self.loop.update_positions(positions)

            # ---- 3. Call volatility models ----
            vol_signals = []
            for vm in self.vol_models:
                signal = vm.update(state)
                if signal:
                    vol_signals.append(signal)

            # ---- 4. Create strategy context ----
            ctx = StrategyContext(state=state, vol_signals=vol_signals)

            # ---- 5. Let strategies respond ----
            actions: List[TradeAction] = []
            for strategy in self.strategies:
                # Tick-based adjustments
                tick_actions = strategy.on_tick(ctx)
                actions.extend(tick_actions)

                # Reaction to vol signals
                for _ in vol_signals:
                    signal_actions = strategy.on_vol_signal(ctx)
                    actions.extend(signal_actions)

            # ---- 6. Run actions through a risk manager ----
            safe_actions = self.risk_mgr.filter_actions(actions)

            # ---- 7. (Step 1) DO NOT EXECUTE ORDERS YET ----
            if safe_actions:
                print("\n=== ACTIONS GENERATED ===")
                for action in safe_actions:
                    print(action)
                print("=========================\n")