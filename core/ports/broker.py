"""
Domain ports for execution brokers.
"""
from abc import ABC, abstractmethod
from typing import List
from core.domain.types import OrderRequest, OrderExecutionReport, Position

class Broker(ABC):
    """Abstract base class for execution brokers."""

    @abstractmethod
    def place_order(self, order: OrderRequest) -> OrderExecutionReport:
        """Place a new order."""

    @abstractmethod
    def modify_order(self, order_id: str, **kwargs) -> OrderExecutionReport:
        """Modify an existing order."""

    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        """Cancel an existing order."""

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Get all open positions."""