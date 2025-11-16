from abc import ABC, abstractmethod
from typing import List
from core.domain.types import OrderRequest, OrderExecutionReport, Position

class Broker(ABC):

    @abstractmethod
    def place_order(self, order: OrderRequest) -> OrderExecutionReport:
        ...

    @abstractmethod
    def modify_order(self, order_id: str, **kwargs) -> OrderExecutionReport:
        ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        ...

    @abstractmethod
    def get_positions(self) -> List[Position]:
        ...