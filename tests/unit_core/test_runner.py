import unittest
from unittest.mock import MagicMock
from core.engine.runner import Engine
from core.domain.types import Tick
from core.domain.actions import TradeAction
from core.domain.signals import VolSignal

from datetime import datetime

class TestRunner(unittest.TestCase):
    def test_run_orchestration(self):
        # Mocks
        feed = MagicMock()
        broker = MagicMock()
        vol_model = MagicMock()
        strategy = MagicMock()
        risk_mgr = MagicMock()
        
        # Setup Feed
        tick = Tick(123, datetime.now(), 100.0, 10) # Minimal tick
        feed.stream.return_value = [tick] # Yield one tick then exit
        
        # Setup Broker
        broker.get_positions.return_value = []
        
        # Setup VolModel
        sig = VolSignal(123, "VOL_UP", 0.5, 1000)
        vol_model.update.return_value = sig
        
        # Setup Strategy
        action = TradeAction("BUY", 123, 1, {})
        strategy.on_tick.return_value = []
        strategy.on_vol_signal.return_value = [action]
        
        # Setup Risk
        risk_mgr.filter_actions.return_value = [action]
        
        engine = Engine(feed, broker, [vol_model], [strategy], risk_mgr)
        
        # Capture print output? Or just verify calls
        # Run
        engine.run()
        
        # Verify Interactions
        feed.stream.assert_called_once()
        broker.get_positions.assert_called()
        vol_model.update.assert_called()
        strategy.on_vol_signal.assert_called()
        risk_mgr.filter_actions.assert_called_with([action])

if __name__ == "__main__":
    unittest.main()
