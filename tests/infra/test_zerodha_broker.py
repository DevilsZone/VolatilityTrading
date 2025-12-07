import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock kiteconnect module
mock_kite_module = MagicMock()
sys.modules["kiteconnect"] = mock_kite_module

from infra.zerodtha.zerodtha_broker import ZerodhaBroker
from core.domain.types import OrderRequest

class TestZerodhaBroker(unittest.TestCase):
    @patch("infra.zerodtha.zerodtha_broker.KiteConnect")
    def test_place_order(self, MockKite):
        mock_kite = MockKite.return_value
        broker = ZerodhaBroker("api_key", "access_token")
        mock_kite.place_order.return_value = "order_123"
        
        order = OrderRequest(
            instrument_token=123,
            quantity=10,
            transaction_type="BUY",
            order_type="LIMIT",
            price=100.0
        )
        
        report = broker.place_order(order)
        
        self.assertEqual(report.order_id, "order_123")
        self.assertEqual(report.status, "NEW")
        mock_kite.place_order.assert_called_once()

    @patch("infra.zerodtha.zerodtha_broker.KiteConnect")
    def test_get_positions(self, MockKite):
        mock_kite = MockKite.return_value
        broker = ZerodhaBroker("api_key", "access_token")
        mock_kite.positions.return_value = {
            "net": [
                {
                    "instrument_token": 123,
                    "quantity": 50,
                    "average_price": 100.0,
                    "pnl": 500.0
                }
            ]
        }
        
        positions = broker.get_positions()
        
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].instrument_token, 123)
        self.assertEqual(positions[0].quantity, 50)
        self.assertEqual(positions[0].pnl, 500.0)

if __name__ == "__main__":
    unittest.main()
