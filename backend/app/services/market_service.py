"""Market data service.

This service provides a unified interface for market data,
delegating to configurable data source adapters.

Architecture:
    API Request -> MarketService -> DataSourceAdapter -> External API
                              |
                              v
                      MarketDataFormatter
                              |
                              v
                         System Schema
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional

from app.config import settings
from app.services.adapters import get_adapter, DataSourceAdapter, RawQuoteData, RawKlineData, RawSearchResult


class MarketDataFormatter:
    """Formats raw adapter data to system schema format."""

    @staticmethod
    def format_quote(raw: RawQuoteData) -> Dict[str, Any]:
        """Format raw quote to API response schema.

        Returns dict matching QuoteResponse schema.
        """
        return {
            "symbol": raw.symbol,
            "name": raw.name,
            "price": raw.price,
            "change": raw.change,
            "change_pct": raw.change_pct,
            "volume": raw.volume,
            "amount": raw.amount,
            "high": raw.high,
            "low": raw.low,
            "open": raw.open,
            "close": raw.close,
            "timestamp": raw.timestamp,
        }

    @staticmethod
    def format_kline(raw: RawKlineData) -> Dict[str, Any]:
        """Format raw kline to API response schema.

        Returns dict matching KlineResponse schema.
        """
        return {
            "dates": [MarketDataFormatter._to_str(d) for d in raw.dates],
            "opens": [MarketDataFormatter._to_float(v) for v in raw.opens],
            "highs": [MarketDataFormatter._to_float(v) for v in raw.highs],
            "lows": [MarketDataFormatter._to_float(v) for v in raw.lows],
            "closes": [MarketDataFormatter._to_float(v) for v in raw.closes],
            "volumes": [MarketDataFormatter._to_float(v) for v in raw.volumes],
        }

    @staticmethod
    def format_search(raw_list: List[RawSearchResult]) -> List[Dict[str, str]]:
        """Format raw search results to API response schema.

        Returns list matching List[SearchResult] schema.
        """
        return [
            {
                "code": r.code,
                "name": r.name,
                "market": r.market,
                "type": "stock",
            }
            for r in raw_list
        ]

    @staticmethod
    def _to_str(v: Any) -> str:
        """Convert value to string (for dates)."""
        if isinstance(v, str):
            return v
        elif isinstance(v, (datetime, date)):
            return v.strftime('%Y-%m-%d')
        return str(v)

    @staticmethod
    def _to_float(v: Any) -> float:
        """Convert value to float safely."""
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0


class MarketService:
    """Main service for market data operations.

    Uses a configurable data source adapter and formats data to system schema.

    Usage:
        # Use default data source from settings
        service = MarketService()
        quote = await service.get_quote("000001.SZ")

        # Use specific data source
        service = MarketService(data_source="tushare")
        quote = await service.get_quote("000001.SZ")
    """

    def __init__(self, data_source: Optional[str] = None):
        """Initialize market service.

        Args:
            data_source: Name of data source ('akshare', 'tushare').
                        Defaults to settings.DATA_SOURCE.
        """
        self.data_source = data_source or settings.DATA_SOURCE
        self.adapter: DataSourceAdapter = get_adapter(self.data_source)
        self.formatter = MarketDataFormatter()

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol.

        Args:
            symbol: Stock code in format '000001.SZ' or '600000.SH'

        Returns:
            Quote data in system schema format (QuoteResponse)
        """
        raw = await self.adapter.get_quote(symbol)
        return self.formatter.format_quote(raw)

    async def get_quotes(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get quotes for multiple symbols.

        Args:
            symbols: List of stock codes

        Returns:
            List of quote data in system schema format
        """
        results = []
        for symbol in symbols:
            try:
                quote = await self.get_quote(symbol)
                results.append(quote)
            except Exception:
                continue
        return results

    async def get_kline(
        self, symbol: str, period: str = "daily",
        start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get kline data for a symbol.

        Args:
            symbol: Stock code in format '000001.SZ' or '600000.SH'
            period: 'daily' or 'weekly'
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format

        Returns:
            Kline data in system schema format (KlineResponse)
        """
        raw = await self.adapter.get_kline(symbol, period, start_date, end_date)
        return self.formatter.format_kline(raw)

    async def search(self, keyword: str) -> List[Dict[str, str]]:
        """Search stocks by keyword.

        Args:
            keyword: Stock code (e.g., '000001' or '000001.SZ')

        Returns:
            List of search results in system schema format (List[SearchResult])
        """
        raw_results = await self.adapter.search(keyword)
        return self.formatter.format_search(raw_results)

    async def get_historical_full(
        self,
        symbol: str,
        period: str = "daily",
        years: int = 10
    ) -> Dict[str, Any]:
        """Get full historical kline data from many years ago to now.

        Use this for initial data load or full refresh.

        Args:
            symbol: Stock code in format '000001.SZ' or '600000.SH'
            period: 'daily' or 'weekly'
            years: Number of years of history to fetch (default 10)

        Returns:
            Kline data in system schema format with all historical data
        """
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y%m%d')

        raw = await self.adapter.get_kline(symbol, period, start_date, end_date)
        return self.formatter.format_kline(raw)

    async def get_historical_incremental(
        self,
        symbol: str,
        last_date: str,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """Get incremental kline data since last update.

        Use this for daily updates after initial load.
        Returns data from last_date (exclusive) to now.

        Args:
            symbol: Stock code in format '000001.SZ' or '600000.SH'
            last_date: Last date already in database (YYYY-MM-DD format)
            period: 'daily' or 'weekly'

        Returns:
            Kline data in system schema format with only new data
        """
        # Convert YYYY-MM-DD to YYYYMMDD for API
        start_date = last_date.replace('-', '')
        end_date = datetime.now().strftime('%Y%m%d')

        raw = await self.adapter.get_kline(symbol, period, start_date, end_date)

        # Filter out the last_date itself (exclusive)
        formatted = self.formatter.format_kline(raw)
        filtered_dates = []
        filtered_opens = []
        filtered_highs = []
        filtered_lows = []
        filtered_closes = []
        filtered_volumes = []

        for i, d in enumerate(formatted['dates']):
            if d > last_date:
                filtered_dates.append(d)
                filtered_opens.append(formatted['opens'][i])
                filtered_highs.append(formatted['highs'][i])
                filtered_lows.append(formatted['lows'][i])
                filtered_closes.append(formatted['closes'][i])
                filtered_volumes.append(formatted['volumes'][i])

        return {
            "dates": filtered_dates,
            "opens": filtered_opens,
            "highs": filtered_highs,
            "lows": filtered_lows,
            "closes": filtered_closes,
            "volumes": filtered_volumes,
        }

    async def batch_get_historical_full(
        self,
        symbols: List[str],
        period: str = "daily",
        years: int = 10
    ) -> Dict[str, Dict[str, Any]]:
        """Get full historical kline data for multiple symbols.

        Args:
            symbols: List of stock codes
            period: 'daily' or 'weekly'
            years: Number of years of history to fetch

        Returns:
            Dict mapping symbol to Kline data
        """
        results = {}
        for symbol in symbols:
            try:
                data = await self.get_historical_full(symbol, period, years)
                results[symbol] = data
            except Exception:
                continue
        return results

    async def batch_get_historical_incremental(
        self,
        last_dates: Dict[str, str],
        period: str = "daily"
    ) -> Dict[str, Dict[str, Any]]:
        """Get incremental kline data for multiple symbols.

        Args:
            last_dates: Dict mapping symbol to last date (YYYY-MM-DD format)
            period: 'daily' or 'weekly'

        Returns:
            Dict mapping symbol to Kline data with only new data
        """
        results = {}
        for symbol, last_date in last_dates.items():
            try:
                data = await self.get_historical_incremental(symbol, last_date, period)
                results[symbol] = data
            except Exception:
                continue
        return results
