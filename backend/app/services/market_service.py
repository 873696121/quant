"""Market data service using akshare (with mock fallback)."""

from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False


# Mock data for when akshare is not available
MOCK_STOCKS = {
    "000001": {"name": "平安银行", "price": 12.50, "change": 0.15, "change_pct": 1.21},
    "000002": {"name": "万科A", "price": 8.80, "change": -0.10, "change_pct": -1.12},
    "600000": {"name": "浦发银行", "price": 7.85, "change": 0.05, "change_pct": 0.64},
    "600519": {"name": "贵州茅台", "price": 1688.00, "change": 15.50, "change_pct": 0.93},
    "600036": {"name": "招商银行", "price": 35.20, "change": -0.30, "change_pct": -0.85},
}


class MarketService:
    """Service for market data operations."""

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol."""
        # Strip suffix
        clean_symbol = symbol.split('.')[0]

        if not HAS_AKSHARE:
            return self._mock_quote(clean_symbol)

        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == clean_symbol]
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
        # Strip suffix
        clean_symbol = symbol.split('.')[0]

        if not HAS_AKSHARE:
            return self._mock_kline(clean_symbol)

        try:
            if period == "daily":
                if start_date and end_date:
                    df = ak.stock_zh_a_hist(symbol=clean_symbol, period="daily", start_date=start_date, end_date=end_date)
                else:
                    df = ak.stock_zh_a_hist(symbol=clean_symbol, period="daily", adjust="qfq")
            elif period == "weekly":
                df = ak.stock_zh_a_hist(symbol=clean_symbol, period="weekly", adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=clean_symbol, period="daily", adjust="qfq")

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
        if not HAS_AKSHARE:
            return self._mock_search(keyword)

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

    def _mock_quote(self, symbol: str) -> Dict[str, Any]:
        """Return mock quote data."""
        if symbol in MOCK_STOCKS:
            stock = MOCK_STOCKS[symbol]
            return {
                "symbol": symbol,
                "name": stock["name"],
                "price": stock["price"],
                "change": stock["change"],
                "change_pct": stock["change_pct"],
                "volume": 1000000,
                "amount": stock["price"] * 1000000,
                "high": stock["price"] * 1.02,
                "low": stock["price"] * 0.98,
                "open": stock["price"] * 0.99,
                "close": stock["price"] - stock["change"],
                "timestamp": datetime.now().isoformat(),
            }
        raise ValueError(f"Symbol {symbol} not found")

    def _mock_kline(self, symbol: str) -> Dict[str, Any]:
        """Return mock K-line data."""
        import random
        base_price = 10.0
        dates = [(datetime.now().replace(hour=0, minute=0, second=0)).strftime('%Y-%m-%d')]

        if symbol in MOCK_STOCKS:
            base_price = MOCK_STOCKS[symbol]["price"]

        dates = [(datetime.now().replace(day=i, hour=0, minute=0, second=0)).strftime('%Y-%m-%d')
                 for i in range(1, 21)]
        dates.reverse()

        closes = []
        opens = []
        highs = []
        lows = []
        volumes = []

        price = base_price * 0.9
        for _ in range(20):
            open_p = price * (1 + random.uniform(-0.02, 0.02))
            close_p = open_p * (1 + random.uniform(-0.02, 0.02))
            high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.01))
            low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.01))
            vol = int(random.uniform(500000, 5000000))

            opens.append(round(open_p, 2))
            closes.append(round(close_p, 2))
            highs.append(round(high_p, 2))
            lows.append(round(low_p, 2))
            volumes.append(vol)
            price = close_p

        return {
            "dates": dates,
            "opens": opens,
            "highs": highs,
            "lows": lows,
            "closes": closes,
            "volumes": volumes,
        }

    def _mock_search(self, keyword: str) -> List[Dict[str, str]]:
        """Return mock search results."""
        results = []
        for code, info in MOCK_STOCKS.items():
            if keyword in code or keyword in info["name"]:
                results.append({
                    "code": code,
                    "name": info["name"],
                    "market": "SH" if code.startswith("6") else "SZ",
                    "type": "stock",
                })
        return results
