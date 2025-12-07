"""
The event loop module manages the market state updates.
"""
# core/engine/event_loop.py

from typing import Dict, List
from core.domain.state import MarketState
from core.domain.types import Tick, Candle


class EventLoop:
    """
    Maintains the current market state.
    Turns all incoming ticks into updated MarketState objects.
    """

    def __init__(self):
        self.state = MarketState(
            last_ticks={},         # instrument_token → Tick
            recent_candles={},     # instrument_token → list[Candle]
            positions={},          # instrument_token → quantity
            timestamp=0
        )

    def update_state_with_tick(self, tick: Tick) -> MarketState:
        """
        Update the latest tick for the instrument.
        """
        self.state.last_ticks[tick.instrument_token] = tick
        self.state.timestamp = tick.timestamp.timestamp()
        return self.state

    def update_positions(self, positions: Dict[int, int]):
        """Update current position quantities."""
        self.state.positions = positions
        return self.state

    def set_candles(self, instrument_token: int, candles: List[Candle]):
        """Update recent candles for an instrument."""
        self.state.recent_candles[instrument_token] = candles

    def get_state(self) -> MarketState:
        """Return the current market state."""
        return self.state