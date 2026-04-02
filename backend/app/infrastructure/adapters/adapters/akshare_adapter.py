"""Akshare data source adapter."""

import os
from datetime import datetime
from typing import List, Optional, Any

import akshare as ak

from .base import DataSourceAdapter, RawQuoteData, RawKlineData, RawSearchResult


class AkshareAdapter(DataSourceAdapter):
    """Akshare implementation of DataSourceAdapter.

    Uses Tencent K-line API (stock_zh_a_hist_tx) for reliable data access.
    """

    @property
    def name(self) -> str:
        return "akshare"

    def _clear_proxy(self):
        """Clear proxy environment variables for this request."""
        for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
            os.environ.pop(k, None)

    def _symbol_to_market(self, symbol: str) -> tuple:
        """Convert symbol to market prefix for Tencent API.

        Returns:
            (clean_symbol, market_prefix) e.g. ('000001', 'sz')
        """
        clean = symbol.split('.')[0]
        if symbol.endswith('.SH'):
            return clean, 'sh'
        elif symbol.endswith('.SZ'):
            return clean, 'sz'
        else:
            if clean.startswith(('6', '5')):
                return clean, 'sh'
            return clean, 'sz'

    def _to_float(self, v: Any) -> float:
        """Convert value to float safely."""
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    async def get_quote(self, symbol: str) -> RawQuoteData:
        """Get real-time quote using Tencent K-line data.

        Since Tencent API doesn't provide real-time quote,
        we get latest K-line data as a proxy for quote info.
        """
        self._clear_proxy()
        clean_symbol, market_prefix = self._symbol_to_market(symbol)

        try:
            df = ak.stock_zh_a_hist_tx(
                symbol=f"{market_prefix}{clean_symbol}",
                start_date="20260401",
                end_date="20500101",
                adjust="qfq"
            )
            if df.empty:
                raise ValueError(f"Symbol {symbol} not found")

            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            change = self._to_float(latest['close']) - self._to_float(prev['close'])
            prev_close = self._to_float(prev['close'])
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0.0

            return RawQuoteData(
                symbol=symbol,
                name="",  # Would need separate call for name
                price=self._to_float(latest['close']),
                change=change,
                change_pct=round(change_pct, 2),
                volume=0,  # K-line doesn't have volume in same units
                amount=self._to_float(latest['amount']),
                high=self._to_float(latest['high']),
                low=self._to_float(latest['low']),
                open=self._to_float(latest['open']),
                close=self._to_float(latest['close']),
                timestamp=datetime.now().isoformat(),
            )
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Akshare quote failed: {str(e)}")

    async def get_kline(
        self, symbol: str, period: str = "daily",
        start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> RawKlineData:
        """Get kline data using Tencent K-line API."""
        self._clear_proxy()
        clean_symbol, market_prefix = self._symbol_to_market(symbol)

        try:
            if not start_date:
                start_date = "20250101"
            if not end_date:
                end_date = "20500101"

            df = ak.stock_zh_a_hist_tx(
                symbol=f"{market_prefix}{clean_symbol}",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="qfq"
            )

            if df.empty:
                raise ValueError(f"Symbol {symbol} not found")

            return RawKlineData(
                dates=df['date'].tolist(),
                opens=df['open'].tolist(),
                highs=df['high'].tolist(),
                lows=df['low'].tolist(),
                closes=df['close'].tolist(),
                volumes=df['amount'].tolist(),
            )
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Akshare kline failed: {str(e)}")

    async def search(self, keyword: str) -> List[RawSearchResult]:
        """Search stocks by code using Tencent K-line API."""
        self._clear_proxy()
        clean_keyword = keyword.split('.')[0]

        if not (clean_keyword.isdigit() and len(clean_keyword) == 6):
            raise ValueError(f"Invalid stock code: {keyword}")

        market_prefix = 'sh' if clean_keyword.startswith(('6', '5')) else 'sz'
        market = 'SH' if clean_keyword.startswith(('6', '5')) else 'SZ'

        try:
            df = ak.stock_zh_a_hist_tx(
                symbol=f"{market_prefix}{clean_keyword}",
                start_date="20260401",
                end_date="20500101",
                adjust="qfq"
            )

            if df.empty:
                raise ValueError(f"No stock found for: {keyword}")

            return [RawSearchResult(
                code=f"{clean_keyword}.{market}",
                name="",  # Would need separate call for name
                market=market,
            )]
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Akshare search failed: {str(e)}")
