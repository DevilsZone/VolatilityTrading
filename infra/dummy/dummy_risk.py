# infra/dummy/dummy_risk.py

from core.ports.risk import RiskManager


class DummyRiskManager(RiskManager):

    def filter_actions(self, actions):
        # allow all actions
        return actions