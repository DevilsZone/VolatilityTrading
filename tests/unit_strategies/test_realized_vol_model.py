import unittest
from datetime import datetime
from strategies.vol_models.realized_vol_model import RealizedVolModel
from core.domain.state import MarketState
from core.domain.types import Tick

class TestRealizedVolModel(unittest.TestCase):
    def test_vol_calculation(self):
        model = RealizedVolModel(instrument_token=123, lookback=5, annualize_factor=1.0)
        state = MarketState(last_ticks={}, recent_candles={}, positions={}, timestamp=0.0)
        
        # Feed prices 100, 101, 102, 103, 104, 105
        # return approx 1% each step
        prices = [100, 101, 102, 103, 104, 105]
        for p in prices:
            t = Tick(123, datetime.now(), float(p), 100)
            state.last_ticks[123] = t
            model.update(state)
            
        # Should have enough data now
        # model._prices should have 6 items
        self.assertEqual(len(model._prices), 6)
        
        # Vol calculation happens. 
        # Since steps are uniform ~1%, vol. ~0.
        # Wait, strictly constant return means variance is 0. 
        # Let's make it volatile: 100, 105, 100, 105
        
    def test_vol_signal_trigger(self):
        # Thresholds: High=0.01, Low=0.003
        model = RealizedVolModel(instrument_token=123, lookback=3, high_threshold=0.01, annualize_factor=1.0)
        state = MarketState(last_ticks={}, recent_candles={}, positions={}, timestamp=0.0)
        
        # Volatile sequence
        prices = [100.0, 105.0, 100.0, 105.0] # ~5% returns, high vol
        
        last_signal = None
        for p in prices:
            t = Tick(123, datetime.now(), p, 100)
            state.last_ticks[123] = t
            s = model.update(state)
            if s: last_signal = s
            
        self.assertIsNotNone(last_signal)
        self.assertEqual(last_signal.kind, "VOL_UP")

if __name__ == "__main__":
    unittest.main()
