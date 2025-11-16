import uuid
from datetime import datetime, timezone
from typing import List

from core.ports.broker import Broker
from core.domain.types import OrderRequest, OrderExecutionReport, Position


class DummyBroker(Broker):

    def __init__(self):
        self.positions = {}   # token → Position
        self.orders = {}      # order_id → OrderExecutionReport

    def place_order(self, order: OrderRequest) -> OrderExecutionReport:
        order_id = str(uuid.uuid4())
        fill_price = order.price or 100.0  # dummy fill

        # BUY → +qty, SELL → -qty
        mult = 1 if order.transaction_type == "BUY" else -1
        qty_change = mult * order.quantity

        # Update position
        if order.instrument_token in self.positions:
            pos = self.positions[order.instrument_token]
            new_qty = pos.quantity + qty_change
            avg_price = fill_price if new_qty == qty_change else pos.avg_price
        else:
            new_qty = qty_change
            avg_price = fill_price

        # For DummyBroker, unrealized PnL = 0
        self.positions[order.instrument_token] = Position(
            instrument_token=order.instrument_token,
            quantity=new_qty,
            avg_price=avg_price,
            pnl=0.0
        )

        report = OrderExecutionReport(
            order_id=order_id,
            status="FILLED",
            filled_quantity=order.quantity,
            avg_price=fill_price,
            timestamp=datetime.now(timezone.utc)
        )

        self.orders[order_id] = report
        return report

    def modify_order(self, order_id: str, **kwargs) -> OrderExecutionReport:
        return self.orders[order_id]

    def cancel_order(self, order_id: str) -> None:
        pass  # instant fills cannot be canceled

    def get_positions(self) -> List[Position]:
        return list(self.positions.values())