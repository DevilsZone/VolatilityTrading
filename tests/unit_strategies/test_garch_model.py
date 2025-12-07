import unittest
from datetime import datetime
from strategies.vol_models.garch_vol_model import GARCHVolModel
from core.domain.state import MarketState
from core.domain.types import Tick

class TestGARCHVolModel(unittest.TestCase):
    def test_recursion(self):
        omega = 0.000001
        alpha = 0.1
        beta = 0.8
        model = GARCHVolModel(instrument_token=123, omega=omega, alpha=alpha, beta=beta, annualize_factor=1.0)
        
        # Check initial variance seed
        expected_long_run_var = omega / (1 - alpha - beta)
        self.assertAlmostEqual(model.current_variance, expected_long_run_var, places=6)
        
        state = MarketState(last_ticks={}, recent_candles={}, positions={}, timestamp=None)
        t1 = Tick(123, datetime.now(), 100.0, 100)
        state.last_ticks[123] = t1
        model.update(state)
        
        # Second tick
        t2 = Tick(123, datetime.now(), 101.0, 100)
        state.last_ticks[123] = t2
        model.update(state)
        
        # Variance should have changed
        self.assertNotEqual(model.current_variance, expected_long_run_var)

if __name__ == "__main__":
    unittest.main()
