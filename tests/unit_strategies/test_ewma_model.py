import unittest
from datetime import datetime
from strategies.vol_models.ewma_vol_model import EWMAVolModel
from core.domain.state import MarketState
from core.domain.types import Tick

class TestEWMAVolModel(unittest.TestCase):
    def test_update_variance(self):
        model = EWMAVolModel(instrument_token=123, decay_factor=0.9, annualize_factor=1.0)
        state = MarketState(last_ticks={}, recent_candles={}, positions={}, timestamp=0.0)
        
        # 1. First tick (sets last_price)
        t1 = Tick(123, datetime.now(), 100.0, 100)
        state.last_ticks[123] = t1
        signal = model.update(state)
        self.assertIsNone(signal)
        self.assertEqual(model.last_price, 100.0)
        
        # 2. Second tick (init variance)
        # log return = log(101/100) ~ 0.00995
        # variance = return^2 ~ 0.000099
        t2 = Tick(123, datetime.now(), 101.0, 100)
        state.last_ticks[123] = t2
        model.update(state)
        
        self.assertTrue(model.initialized)
        self.assertGreater(model.current_variance, 0.0)

    def test_signal_emission(self):
        # Set a high threshold low to force a signal
        model = EWMAVolModel(instrument_token=123, high_threshold=0.0001, annualize_factor=1.0)
        state = MarketState(last_ticks={}, recent_candles={}, positions={}, timestamp=0.0)
        
        t1 = Tick(123, datetime.now(), 100.0, 100)
        state.last_ticks[123] = t1
        model.update(state)
        
        t2 = Tick(123, datetime.now(), 105.0, 100)
        state.last_ticks[123] = t2
        signal = model.update(state)
        
        self.assertIsNotNone(signal)
        self.assertEqual(signal.kind, "VOL_UP")

if __name__ == "__main__":
    unittest.main()
