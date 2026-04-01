"""Market data service using akshare."""

from typing import List, Optional, Dict, Any
import akshare as ak
from datetime import datetime


class MarketService:
    """Service for market data operations."""

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol."""
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == symbol]
            if row.empty:
                raise ValueError(f"Symbol {symbol} not found")

            row = row.iloc[0]
            return {
                "symbol": symbol,
                "name": row['名称'],
                "price": float(row['最新价']),
                "change": float(row['涨跌额']),
                "change_pct": float(row['涨跌幅']),
                "volume": int(row['成交量']),
                "amount": float(row['成交额']),
                "high": float(row['最高']),
                "low": float(row['最低']),
                "open": float(row['今开']),
                "close": float(row['昨收']),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            raise ValueError(f"Failed to get quote: {str(e)}")

    async def get_quotes(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get quotes for multiple symbols."""
        results = []
        for symbol in symbols:
            try:
                quote = await self.get_quote(symbol)
                results.append(quote)
            except Exception:
                continue
        return results

    async def get_kline(
        self, symbol: str, period: str = "daily", start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get kline data for a symbol."""
        try:
            if period == "daily":
                if start_date and end_date:
                    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
                else:
                    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            elif period == "weekly":
                df = ak.stock_zh_a_hist(symbol=symbol, period="weekly", adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")

            return {
                "dates": df['日期'].tolist(),
                "opens": df['开盘'].tolist(),
                "highs": df['最高'].tolist(),
                "lows": df['最低'].tolist(),
                "closes": df['收盘'].tolist(),
                "volumes": df['成交量'].tolist(),
            }
        except Exception as e:
            raise ValueError(f"Failed to get kline: {str(e)}")

    async def search(self, keyword: str) -> List[Dict[str, str]]:
        """Search stocks by keyword."""
        try:
            df = ak.stock_zh_a_spot_em()
            mask = df['名称'].str.contains(keyword, na=False) | df['代码'].str.contains(keyword, na=False)
            results = df[mask].head(20)

            return [
                {
                    "code": row['代码'],
                    "name": row['名称'],
                    "market": row['市场'],
                    "type": "stock",
                }
                for _, row in results.iterrows()
            ]
        except Exception as e:
            raise ValueError(f"Failed to search: {str(e)}")
