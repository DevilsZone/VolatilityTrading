import unittest
from unittest.mock import MagicMock, patch
import threading
import time
import sys

# Mock kiteconnect module
mock_kite_module = MagicMock()
sys.modules["kiteconnect"] = mock_kite_module

from infra.zerodtha.zerodtha_feed import ZerodhaFeed

class TestZerodhaFeed(unittest.TestCase):
    @patch("infra.zerodtha.zerodtha_feed.KiteTicker")
    def test_subscribe(self, MockTicker):
        instance = MockTicker.return_value
        instance.is_connected.return_value = True
        
        feed = ZerodhaFeed("key", "token")
        feed.subscribe([123, 456])
        
        instance.subscribe.assert_called_with([123, 456])
        instance.set_mode.assert_called()

    @patch("infra.zerodtha.zerodtha_feed.KiteTicker")
    def test_stream_ticks(self, MockTicker):
        # Mocking the ticker instance
        instance = MockTicker.return_value
        
        feed = ZerodhaFeed("key", "token")
        
        # Simulate on_ticks callback
        ticks = [{
            "instrument_token": 123, 
            "last_price": 100.0, 
            "volume": 1000, 
            "timestamp": "2024-01-01",
            "volume": 500
        }]
        
        def simulate_ticks():
            time.sleep(0.1)
            feed._on_ticks(instance, ticks)
            
        t = threading.Thread(target=simulate_ticks)
        t.start()
        
        # consume stream
        stream = feed.stream()
        tick = next(stream)
        
        self.assertEqual(tick.instrument_token, 123)
        self.assertEqual(tick.last_price, 100.0)
        self.assertEqual(tick.volume, 500)
        
        t.join()

if __name__ == "__main__":
    unittest.main()
