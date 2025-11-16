import uuid
from typing import List
from datetime import datetime, timezone

from core.ports.broker import Broker
from core.domain.types import OrderRequest, OrderExecutionReport, Position


class SimulatedBroker(Broker):
    """
    Backtest broker. Orders remain NEW until the backtest engine fills them.
    """

    def __init__(self):
        self.positions = {}         # token → Position
        self.orders = {}            # order_id → OrderExecutionReport
        self.pending_orders = {}    # order_id → OrderRequest

    def place_order(self, order: OrderRequest) -> OrderExecutionReport:
        order_id = str(uuid.uuid4())

        report = OrderExecutionReport(
            order_id=order_id,
            status="NEW",
            filled_quantity=0,
            avg_price=0.0,
            timestamp=datetime.now(timezone.utc)
        )

        self.orders[order_id] = report
        self.pending_orders[order_id] = order
        return report

    def modify_order(self, order_id: str, **kwargs) -> OrderExecutionReport:
        order = self.pending_orders.get(order_id)
        if order:
            for key, value in kwargs.items():
                if hasattr(order, key):
                    object.__setattr__(order, key, value)
        return self.orders[order_id]

    def cancel_order(self, order_id: str) -> None:
        if order_id in self.pending_orders:
            del self.pending_orders[order_id]
        if order_id in self.orders:
            self.orders[order_id].status = "CANCELLED"

    def get_positions(self) -> List[Position]:
        return list(self.positions.values())

    # ------------ CALLED BY BACKTEST ENGINE -----------------

    def _simulate_fill(self, order_id: str, fill_price: float, fill_qty: int):
        """
        Backtest engine provides fill price and quantity.
        """

        order_req = self.pending_orders.get(order_id)
        if not order_req:
            return

        report = self.orders[order_id]

        mult = 1 if order_req.transaction_type == "BUY" else -1
        qty_delta = mult * fill_qty

        if order_req.instrument_token in self.positions:
            pos = self.positions[order_req.instrument_token]
            new_qty = pos.quantity + qty_delta
            avg_price = fill_price if new_qty == qty_delta else pos.avg_price
        else:
            new_qty = qty_delta
            avg_price = fill_price

        # PnL is computed later by the backtest engine normally
        self.positions[order_req.instrument_token] = Position(
            instrument_token=order_req.instrument_token,
            quantity=new_qty,
            avg_price=avg_price,
            pnl=0.0,
        )

        report.filled_quantity = fill_qty
        report.avg_price = fill_price
        report.status = "FILLED"
        report.timestamp = datetime.now(timezone.utc)

        del self.pending_orders[order_id]