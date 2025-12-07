"""
Domain ports for risk management.
"""
from abc import ABC, abstractmethod
from typing import List
from core.domain.actions import TradeAction

class RiskManager(ABC):
    """Abstract base class for risk managers."""

    @abstractmethod
    def filter_actions(self, actions: List[TradeAction]) -> List[TradeAction]:
        """
        Enforce:
          - max position
          - max loss
          - margin limits
          - timing rules
        """