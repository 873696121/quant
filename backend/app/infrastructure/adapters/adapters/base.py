"""Base classes and data types for market data adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Any


@dataclass
class RawQuoteData:
    """Raw quote data from data source."""
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


@dataclass
class RawKlineData:
    """Raw kline data from data source."""
    dates: List[Any]  # Can be str, date, or datetime
    opens: List[Any]
    highs: List[Any]
    lows: List[Any]
    closes: List[Any]
    volumes: List[Any]


@dataclass
class RawSearchResult:
    """Raw search result from data source."""
    code: str
    name: str
    market: str


class DataSourceAdapter(ABC):
    """Abstract interface for market data sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the adapter name."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> RawQuoteData:
        """Get real-time quote for a symbol.

        Args:
            symbol: Stock code in format '000001.SZ' or '600000.SH'

        Returns:
            RawQuoteData with quote information
        """
        pass

    @abstractmethod
    async def get_kline(
        self, symbol: str, period: str = "daily",
        start_date: str = None, end_date: str = None
    ) -> RawKlineData:
        """Get kline data for a symbol.

        Args:
            symbol: Stock code in format '000001.SZ' or '600000.SH'
            period: 'daily' or 'weekly'
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format

        Returns:
            RawKlineData with kline information
        """
        pass

    @abstractmethod
    async def search(self, keyword: str) -> List[RawSearchResult]:
        """Search stocks by keyword.

        Args:
            keyword: Search keyword (stock code or name)

        Returns:
            List of RawSearchResult
        """
        pass
