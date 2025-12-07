"""
Domain types for the trading system.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Tick:
    """Represents a market tick update."""
    instrument_token: int
    timestamp: datetime
    last_price: float
    volume: int
    oi: Optional[int] = None

@dataclass(frozen=True)
class Candle:
    """Represents a market candle (OHLCV) update."""
    instrument_token: int
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: Optional[int] = None

@dataclass(frozen=True)
class OrderRequest:
    """Represents a request to place an order."""
    instrument_token: int
    quantity: int
    order_type: str        # MARKET, LIMIT
    transaction_type: str  # BUY/SELL
    price: Optional[float] = None

@dataclass(frozen=True)
class OrderExecutionReport:
    """Represents a report of an order execution."""
    order_id: str
    status: str            # FILLED, REJECTED, CANCELLED
    filled_quantity: int
    avg_price: float
    timestamp: datetime

@dataclass(frozen=True)
class Position:
    """Represents a current holding position."""
    instrument_token: int
    quantity: int
    avg_price: float
    pnl: float