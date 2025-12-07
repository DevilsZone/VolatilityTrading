"""
Strategy implementation: High volatility long straddle.
"""
from typing import List, Optional

from core.ports.strategy import Strategy, StrategyContext
from core.domain.actions import TradeAction
from core.domain.signals import VolSignal


class HighVolLongStraddleStrategy(Strategy):
    """
    When volatility goes up (VOL_UP), enter a long straddle.
    When volatility goes down (VOL_DOWN), exit.

    NOTE: For now we issue actions on the underlying token itself.
    Later an option resolver will translate metadata into actual
    option instrument tokens.
    """

    name = "high_vol_long_straddle"

    def __init__(
        self,
        underlying_token: int,
        entry_threshold: float = 0.6,
        exit_threshold: float = 0.3,
        lot_size: int = 1,
    ):
        self.underlying_token = underlying_token
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.lot_size = lot_size

        self.position_open: bool = False
        self.last_strike: Optional[float] = None

    def _get_relevant_signal(self, ctx: StrategyContext) -> Optional[VolSignal]:
        """Retrieve the volatility signal for the underlying token."""
        for sig in ctx.vol_signals:
            if sig.instrument_token == self.underlying_token:
                return sig
        return None

    def on_vol_signal(self, ctx: StrategyContext) -> List[TradeAction]:
        """React to a volatility signal."""
        actions: List[TradeAction] = []
        sig = self._get_relevant_signal(ctx)
        if not sig:
            return actions

        tick = ctx.state.last_ticks.get(self.underlying_token)
        if not tick or tick.last_price is None:
            return actions

        ltp = tick.last_price

        # ENTER
        if sig.kind == "VOL_UP" and sig.strength >= self.entry_threshold and not self.position_open:
            self.position_open = True
            self.last_strike = ltp  # placeholder; later round to ATM

            # Here we pretend to open 2 legs; we encode "CE"/"PE" in metadata
            actions.append(
                TradeAction(
                    action_type="OPEN_LONG",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={
                        "structure": "LONG_STRADDLE",
                        "leg": "CALL",
                        "approx_strike": self.last_strike,
                    },
                )
            )
            actions.append(
                TradeAction(
                    action_type="OPEN_LONG",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={
                        "structure": "LONG_STRADDLE",
                        "leg": "PUT",
                        "approx_strike": self.last_strike,
                    },
                )
            )

        # EXIT
        if sig.kind == "VOL_DOWN" and sig.strength <= self.exit_threshold and self.position_open:
            self.position_open = False

            actions.append(
                TradeAction(
                    action_type="CLOSE_LONG",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={
                        "structure": "LONG_STRADDLE",
                        "leg": "CALL",
                        "approx_strike": self.last_strike,
                    },
                )
            )
            actions.append(
                TradeAction(
                    action_type="CLOSE_LONG",
                    instrument_token=self.underlying_token,
                    quantity=self.lot_size,
                    metadata={
                        "structure": "LONG_STRADDLE",
                        "leg": "PUT",
                        "approx_strike": self.last_strike,
                    },
                )
            )

        return actions

    def on_tick(self, ctx: StrategyContext) -> List[TradeAction]:
        """React to market tick updates (not implemented)."""
        # For now, no per-tick management (SL/TP).
        return []