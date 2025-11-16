from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Tick:
    instrument_token: int
    timestamp: datetime
    last_price: float
    volume: int
    oi: Optional[int] = None

@dataclass(frozen=True)
class Candle:
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
    instrument_token: int
    quantity: int
    order_type: str        # MARKET, LIMIT
    transaction_type: str  # BUY/SELL
    price: Optional[float] = None

@dataclass(frozen=True)
class OrderExecutionReport:
    order_id: str
    status: str            # FILLED, REJECTED, CANCELLED
    filled_quantity: int
    avg_price: float
    timestamp: datetime

@dataclass(frozen=True)
class Position:
    instrument_token: int
    quantity: int
    avg_price: float
    pnl: float