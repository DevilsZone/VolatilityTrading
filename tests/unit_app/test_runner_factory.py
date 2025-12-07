import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock kiteconnect and YAML
sys.modules["kiteconnect"] = MagicMock()
sys.modules["yaml"] = MagicMock()

from app.runner_factory import RunnerFactory
from app.config import AppConfig

class TestRunnerFactory(unittest.TestCase):
    def test_build_dummy(self):
        config = AppConfig(mode="dummy", instruments=[123])
        engine = RunnerFactory.build(config)
        
        self.assertIsNotNone(engine)
        self.assertEqual(len(engine.strategies), 1)
        self.assertEqual(len(engine.vol_models), 1)

    @patch("app.runner_factory.ZerodhaBroker")
    @patch("app.runner_factory.ZerodhaFeed")
    def test_build_live(self, MockFeed, MockBroker):
        # Patch the imports inside _build_live if necessary, but since they are imported inside the method,
        # and we are running test, we need to ensure the imports work. 
        # The easiest way is to mock them via sys.modules or assume dependencies exist.
        # Since we mocked them in decorator, let's see. 
        
        config = AppConfig(mode="live", instruments=[123], api_key="k", access_token="t")
        
        # We need to ensure that when RunnerFactory imports infra.zerodtha... it gets our mocks?
        # Standard patch might not work if imports are local.
        # But wait, we can mock `infra.zerodtha.zerodtha_broker` module.
        
        engine = RunnerFactory.build(config)
        
        self.assertIsNotNone(engine)
        MockBroker.assert_called_with("k", "t")
        MockFeed.assert_called_with("k", "t")
        # Check vol models count (Realized + EWMA + GARCH = 3 per token)
        self.assertEqual(len(engine.vol_models), 3)

if __name__ == "__main__":
    unittest.main()
