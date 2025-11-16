# infra/backtest/historical_provider.py

from datetime import datetime
from kiteconnect import KiteConnect

class ZerodhaHistoricalProvider:

    def __init__(self, api_key: str, access_token: str):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

    def get_candles(self, instrument_token: int, start: datetime, end: datetime, interval: str):
        """
        interval: 'minute', '5 minute', '15 minute', 'day', etc.
        """
        return self.kite.historical_data(
            instrument_token,
            start,
            end,
            interval,
            oi=True
        )