"""
Domain ports for strategies.
"""
from abc import ABC, abstractmethod
from typing import List
from core.domain.signals import VolSignal
from core.domain.state import MarketState
from core.domain.actions import TradeAction

class StrategyContext:
    """Context passed to strategies containing market state and signals."""
    def __init__(self, state: MarketState, vol_signals: List[VolSignal]):
        self.state = state
        self.vol_signals = vol_signals

class Strategy(ABC):
    """Abstract base class for trading strategies."""

    name: str = "base_strategy"

    @abstractmethod
    def on_vol_signal(self, ctx: StrategyContext) -> List[TradeAction]:
        ...

    @abstractmethod
    def on_tick(self, ctx: StrategyContext) -> List[TradeAction]:
        ...