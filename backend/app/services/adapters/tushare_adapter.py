"""Tushare data source adapter."""

import os
from datetime import datetime
from typing import List, Optional

from app.config import settings

from .base import DataSourceAdapter, RawQuoteData, RawKlineData, RawSearchResult


class TushareAdapter(DataSourceAdapter):
    """Tushare implementation of DataSourceAdapter.

    Requires TUSHARE_TOKEN to be configured.
    """

    @property
    def name(self) -> str:
        return "tushare"

    def _clear_proxy(self):
        """Clear proxy environment variables for this request."""
        for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
            os.environ.pop(k, None)

    def _get_token(self) -> str:
        """Get Tushare token from settings."""
        token = settings.TUSHARE_TOKEN
        if not token:
            raise ValueError("TUSHARE_TOKEN not configured")
        return token

    def _parse_symbol(self, symbol: str) -> tuple:
        """Parse symbol to Tushare code format.

        Returns:
            (clean_symbol, ts_code) e.g. ('000001', '000001.SZ')
        """
        clean = symbol.split('.')[0]
        if symbol.endswith('.SH'):
            ts_code = f"{clean}.SH"
        elif symbol.endswith('.SZ'):
            ts_code = f"{clean}.SZ"
        else:
            ts_code = f"{clean}.SZ" if not clean.startswith(('6', '5')) else f"{clean}.SH"
        return clean, ts_code

    def _to_float(self, v) -> float:
        """Convert value to float safely."""
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    async def get_quote(self, symbol: str) -> RawQuoteData:
        """Get real-time quote using Tushare."""
        self._clear_proxy()

        try:
            import tushare as ts
            ts.set_token(self._get_token())
            pro = ts.pro_api()

            _, ts_code = self._parse_symbol(symbol)

            df = pro.daily(ts_code=ts_code)
            if df.empty:
                raise ValueError(f"Symbol {symbol} not found")

            row = df.iloc[0]
            close = self._to_float(row.get('close', 0))
            pct_chg = self._to_float(row.get('pct_chg', 0))
            change = close * pct_chg / 100 if pct_chg != 0 else 0

            return RawQuoteData(
                symbol=symbol,
                name="",
                price=close,
                change=change,
                change_pct=pct_chg,
                volume=int(self._to_float(row.get('vol', 0))),
                amount=self._to_float(row.get('amount', 0)),
                high=self._to_float(row.get('high', 0)),
                low=self._to_float(row.get('low', 0)),
                open=self._to_float(row.get('open', 0)),
                close=close,
                timestamp=datetime.now().isoformat(),
            )
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Tushare quote failed: {str(e)}")

    async def get_kline(
        self, symbol: str, period: str = "daily",
        start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> RawKlineData:
        """Get kline data using Tushare."""
        self._clear_proxy()

        try:
            import tushare as ts
            ts.set_token(self._get_token())
            pro = ts.pro_api()

            _, ts_code = self._parse_symbol(symbol)

            if period == "daily":
                df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            elif period == "weekly":
                df = pro.weekly(ts_code=ts_code, start_date=start_date, end_date=end_date)
            else:
                df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

            if df.empty:
                raise ValueError(f"Symbol {symbol} not found")

            # Reverse to chronological order
            df = df.iloc[::-1]

            return RawKlineData(
                dates=df['trade_date'].tolist(),
                opens=df['open'].tolist(),
                highs=df['high'].tolist(),
                lows=df['low'].tolist(),
                closes=df['close'].tolist(),
                volumes=df['vol'].tolist(),
            )
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Tushare kline failed: {str(e)}")

    async def search(self, keyword: str) -> List[RawSearchResult]:
        """Search stocks using Tushare."""
        self._clear_proxy()
        clean_keyword = keyword.split('.')[0]

        if not (clean_keyword.isdigit() and len(clean_keyword) == 6):
            raise ValueError(f"Invalid stock code: {keyword}")

        try:
            import tushare as ts
            ts.set_token(self._get_token())
            pro = ts.pro_api()

            market = 'SH' if clean_keyword.startswith(('6', '5')) else 'SZ'
            ts_code = f"{clean_keyword}.{market}"

            df = pro.daily(ts_code=ts_code)
            if df.empty:
                raise ValueError(f"No stock found for: {keyword}")

            return [RawSearchResult(
                code=f"{clean_keyword}.{market}",
                name="",
                market=market,
            )]
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Tushare search failed: {str(e)}")
