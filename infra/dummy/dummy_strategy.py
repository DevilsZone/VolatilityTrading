# infra/dummy/dummy_strategy.py

from core.ports.strategy import Strategy, StrategyContext
from core.domain.actions import TradeAction


class DummyStrategy(Strategy):

    name = "dummy_strategy"

    def on_vol_signal(self, ctx: StrategyContext):
        actions = []
        for sig in ctx.vol_signals:
            if sig.kind == "VOL_UP":
                # produce a buy action
                actions.append(
                    TradeAction(
                        action_type="OPEN_LONG",
                        instrument_token=sig.instrument_token,
                        quantity=1,
                        price=None
                    )
                )
        return actions

    def on_tick(self, ctx: StrategyContext):
        return []  # do nothing per tick