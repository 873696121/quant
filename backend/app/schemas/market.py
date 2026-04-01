"""Market data schemas."""

from typing import List, Optional
from pydantic import BaseModel


class QuoteResponse(BaseModel):
    """Schema for quote response."""
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float
    volume: int
    amount: float
    high: float
    low: float
    open: float
    close: float
    timestamp: str


class KlineResponse(BaseModel):
    """Schema for kline response."""
    dates: List[str]
    opens: List[float]
    highs: List[float]
    lows: List[float]
    closes: List[float]
    volumes: List[int]


class SearchResult(BaseModel):
    """Schema for stock search result."""
    code: str
    name: str
    market: str
    type: str


class DashboardSummary(BaseModel):
    """Schema for dashboard summary."""
    total_asset: float
    today_profit: float
    position_count: int
    strategy_count: int
    order_count: int


class PositionResponse(BaseModel):
    """Schema for position response."""
    id: int
    symbol: str
    volume: int
    avg_cost: float
    frozen_volume: int
    mode: str
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
