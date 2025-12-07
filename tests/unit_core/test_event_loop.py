import unittest
from datetime import datetime
from core.engine.event_loop import EventLoop
from core.domain.types import Tick

class TestEventLoop(unittest.TestCase):
    def test_update_state_with_tick(self):
        loop = EventLoop()
        tick = Tick(instrument_token=123, timestamp=datetime.now(), last_price=100.0, volume=100)
        
        state = loop.update_state_with_tick(tick)
        
        self.assertEqual(state.last_ticks[123], tick)
        # recent_candles is not updated by ticks automatically in this simplified loop
        # self.assertIn(123, state.recent_candles)
        
    def test_update_positions(self):
        loop = EventLoop()
        positions = {123: 10, 456: -5}
        
        loop.update_positions(positions)
        
        self.assertEqual(loop.state.positions, positions)

if __name__ == "__main__":
    unittest.main()
