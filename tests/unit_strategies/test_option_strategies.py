import unittest
from datetime import datetime
from strategies.option_strategies.high_vol_long_straddle import HighVolLongStraddleStrategy
from core.ports.strategy import StrategyContext
from core.domain.state import MarketState
from core.domain.signals import VolSignal
from core.domain.types import Tick

class TestOptionStrategies(unittest.TestCase):
    def test_straddle_entry(self):
        strat = HighVolLongStraddleStrategy(underlying_token=123, entry_threshold=0.5)
        
        state = MarketState(last_ticks={}, recent_candles={}, positions={}, timestamp=0.0)
        state.last_ticks[123] = Tick(123, datetime.now(), 100.0, 100)
        
        # Signal VOL_UP with 0.8 strength
        sig = VolSignal(123, "VOL_UP", 0.8, datetime.now())
        
        ctx = StrategyContext(state=state, vol_signals=[sig])
        
        actions = strat.on_vol_signal(ctx)
        
        self.assertEqual(len(actions), 2) # Call and Put
        self.assertEqual(actions[0].action_type, "OPEN_LONG")
        self.assertTrue(strat.position_open)

    def test_straddle_exit(self):
        strat = HighVolLongStraddleStrategy(underlying_token=123, exit_threshold=0.4)
        strat.position_open = True
        strat.last_strike = 100.0
        
        state = MarketState(last_ticks={}, recent_candles={}, positions={}, timestamp=0.0)
        state.last_ticks[123] = Tick(123, datetime.now(), 100.0, 100)
        
        # Signal VOL_DOWN with 0.2 strength (below an exit threshold of 0.4 implies? No, wait)
        # Strategy says: if sig.kind == "VOL_DOWN" and sig.strength <= self.exit_threshold,
        # Usually high-strength VOL_DOWN means VERY LOW VOL?
        # Let's check logic: (vol - low) / (high - low).
        # if vol <= low, strength=0. 
        # if vol is dropping, the strength of VOL_UP drops.
        # But RealizedVolModel emits VOL_DOWN when vol <= low_threshold. 
        # And strength calc for VOL_DOWN: 
        #   RealizedVolModel code: if vol <= low: kind=VOL_DOWN. 
        #   Calculates strength based on the same denominator?
        #   Code says: (vol - low) / denominator. If vol < low, this is negative?
        #   Line 91: strength = max(0.0, min(1.0, strength))
        #   So if vol <= low, strength is 0.0. 
        #   Strategy check: if sig.kind == "VOL_DOWN" and sig.strength <= self.exit_threshold
        #   So if VOL_DOWN is emitted, strength is 0. So 0 <= 0.3 is True. 
        
        sig = VolSignal(123, "VOL_DOWN", 0.0, datetime.now())
        ctx = StrategyContext(state=state, vol_signals=[sig])
        
        actions = strat.on_vol_signal(ctx)
        
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].action_type, "CLOSE_LONG")
        self.assertFalse(strat.position_open)

if __name__ == "__main__":
    unittest.main()
