"""
Zerodha implementation of the Broker interface.
"""
from datetime import datetime, timezone
from typing import List

from kiteconnect import KiteConnect

from core.ports.broker import Broker
from core.domain.types import OrderRequest, OrderExecutionReport, Position


class ZerodhaBroker(Broker):
    """Execution broker using Zerodha Kite Connect API."""

    def __init__(self, api_key: str, access_token: str):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

        self.orders = {}  # order_id → OrderExecutionReport

    def place_order(self, order: OrderRequest) -> OrderExecutionReport:
        """Place an order via Kite Connect."""
        transaction = order.transaction_type
        order_type = (
            self.kite.ORDER_TYPE_LIMIT if order.price else self.kite.ORDER_TYPE_MARKET
        )

        order_id = self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange="NFO",
            tradingsymbol=str(order.instrument_token),
            transaction_type=transaction,
            quantity=order.quantity,
            order_type=order_type,
            price=order.price or 0,
            product=self.kite.PRODUCT_MIS,
        )

        report = OrderExecutionReport(
            order_id=order_id,
            status="NEW",
            filled_quantity=0,
            avg_price=0.0,
            timestamp=datetime.now(timezone.utc)
        )

        self.orders[order_id] = report
        return report

    def modify_order(self, order_id: str, **kwargs) -> OrderExecutionReport:
        """Modify an existing order via Kite Connect."""
        self.kite.modify_order(
            variety=self.kite.VARIETY_REGULAR,
            order_id=order_id,
            **kwargs
        )
        return self.orders[order_id]

    def cancel_order(self, order_id: str) -> None:
        """Cancel an order via Kite Connect."""
        self.kite.cancel_order(
            variety=self.kite.VARIETY_REGULAR,
            order_id=order_id
        )
        self.orders[order_id].status = "CANCELLED"

    def get_positions(self) -> List[Position]:
        """Fetch current positions from Zerodha."""
        net = self.kite.positions().get("net", [])
        results = []

        for p in net:
            results.append(
                Position(
                    instrument_token=p["instrument_token"],
                    quantity=p["quantity"],
                    avg_price=p["average_price"],
                    pnl=p["pnl"],
                )
            )
        return results