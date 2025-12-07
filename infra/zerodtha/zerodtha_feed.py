import logging
import queue
from typing import Iterable, List

from kiteconnect import KiteTicker

from core.ports.market_data import MarketDataFeed
from core.domain.types import Tick

logger = logging.getLogger(__name__)


class ZerodhaFeed(MarketDataFeed):
    def __init__(self, api_key: str, access_token: str):
        self.kws = KiteTicker(api_key, access_token)
        self.tick_queue = queue.Queue()
        self.subscribed_tokens = []

        # Bind callbacks
        self.kws.on_ticks = self._on_ticks
        self.kws.on_connect = self._on_connect
        self.kws.on_close = self._on_close
        self.kws.on_error = self._on_error

    def subscribe(self, instruments: List[int]) -> None:
        self.subscribed_tokens = instruments
        # If already connected, subscribe immediately
        if self.kws.is_connected():
            self.kws.subscribe(self.subscribed_tokens)
            self.kws.set_mode(self.kws.MODE_FULL, self.subscribed_tokens)

    def stream(self) -> Iterable[Tick]:
        # Start the ticker in a background thread (non-blocking connect)
        # threaded=True allows it to run in the background while we yield from the queue
        self.kws.connect(threaded=True)

        while True:
            # Blocking get, waiting for ticks
            tick_data = self.tick_queue.get()
            yield tick_data

    def _on_ticks(self, ws, ticks):
        for t in ticks:
            # Transform Kite tick to domain Tick
            # Kite tick structure depends on the mode (Full vs. Quote). Assuming Full/Quote.
            # Common fields: instrument_token, last_price, volume, last_quantity, etc.
            
            # Defensive check for required fields if needed
            timestamp = t.get("timestamp") or t.get("exchange_timestamp")
            
            domain_tick = Tick(
                instrument_token=t["instrument_token"],
                timestamp=timestamp, 
                last_price=t["last_price"],
                volume=t.get("volume", 0),
                oi=t.get("oi", 0)  # Open Interest if available
            )
            self.tick_queue.put(domain_tick)

    def _on_connect(self, ws, response):
        logger.info("Zerodha Ticker connected.")
        if self.subscribed_tokens:
            ws.subscribe(self.subscribed_tokens)
            ws.set_mode(ws.MODE_FULL, self.subscribed_tokens)

    @staticmethod
    def _on_close(ws, code, reason):
        logger.warning(f"Zerodha Ticker closed: {code} - {reason}")

    @staticmethod
    def _on_error(ws, code, reason):
        logger.error(f"Zerodha Ticker error: {code} - {reason}")
