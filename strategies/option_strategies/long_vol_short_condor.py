from typing import List, Optional

from core.ports.strategy import Strategy, StrategyContext
from core.domain.actions import TradeAction
from core.domain.signals import VolSignal


class LowVolShortCondorStrategy(Strategy):
    """
    When volatility is low (VOL_DOWN), enter a short iron condor.
    When volatility increases (VOL_UP), exit.

    This is a *short-vol* strategy and should be used with care.
    """

    name = "low_vol_short_condor"

    def __init__(
        self,
        underlying_token: int,
        width: float = 100.0,
        entry_threshold: float = 0.6,
        exit_threshold: float = 0.3,
        lot_size: int = 1,
    ):
        self.underlying_token = underlying_token
        self.width = width
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.lot_size = lot_size

        self.position_open: bool = False
        self.center_strike: Optional[float] = None

    def _get_relevant_signal(self, ctx: StrategyContext) -> Optional[VolSignal]:
        for sig in ctx.vol_signals:
            if sig.instrument_token == self.underlying_token:
                return sig
        return None

    def on_vol_signal(self, ctx: StrategyContext) -> List[TradeAction]:
        actions: List[TradeAction] = []
        sig = self._get_relevant_signal(ctx)
        if not sig:
            return actions

        tick = ctx.state.last_ticks.get(self.underlying_token)
        if not tick or tick.last_price is None:
            return actions

        ltp = tick.last_price

        # ENTER
        if sig.kind == "VOL_DOWN" and sig.strength >= self.entry_threshold and not self.position_open:
            self.position_open = True
            self.center_strike = ltp

            actions.append(
                TradeAction(
                    action_type="OPEN_SHORT",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={
                        "structure": "IRON_CONDOR",
                        "leg": "SHORT_CALL",
                        "relative_strike": +self.width,
                    },
                )
            )
            actions.append(
                TradeAction(
                    action_type="OPEN_SHORT",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={
                        "structure": "IRON_CONDOR",
                        "leg": "SHORT_PUT",
                        "relative_strike": -self.width,
                    },
                )
            )
            actions.append(
                TradeAction(
                    action_type="OPEN_LONG",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={
                        "structure": "IRON_CONDOR",
                        "leg": "LONG_CALL",
                        "relative_strike": +2 * self.width,
                    },
                )
            )
            actions.append(
                TradeAction(
                    action_type="OPEN_LONG",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={
                        "structure": "IRON_CONDOR",
                        "leg": "LONG_PUT",
                        "relative_strike": -2 * self.width,
                    },
                )
            )

        # EXIT
        if sig.kind == "VOL_UP" and sig.strength <= self.exit_threshold and self.position_open:
            self.position_open = False

            # Reverse all legs
            actions.append(
                TradeAction(
                    action_type="CLOSE_SHORT",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={"structure": "IRON_CONDOR", "leg": "SHORT_CALL"},
                )
            )
            actions.append(
                TradeAction(
                    action_type="CLOSE_SHORT",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={"structure": "IRON_CONDOR", "leg": "SHORT_PUT"},
                )
            )
            actions.append(
                TradeAction(
                    action_type="CLOSE_LONG",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={"structure": "IRON_CONDOR", "leg": "LONG_CALL"},
                )
            )
            actions.append(
                TradeAction(
                    action_type="CLOSE_LONG",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={"structure": "IRON_CONDOR", "leg": "LONG_PUT"},
                )
            )

        return actions

    def on_tick(self, ctx: StrategyContext) -> List[TradeAction]:
        # No intraday adjustment for now
        return []