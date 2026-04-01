"""Market data service using akshare."""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime

import akshare as ak


def _clear_proxy():
    """Clear proxy environment variables for this request."""
    for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
        os.environ.pop(k, None)


class MarketService:
    """Service for market data operations."""

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol.

        Args:
            symbol: Stock code in format '000001.SZ' or '600000.SH'
        """
        _clear_proxy()

        # Strip suffix and determine market
        clean_symbol = symbol.split('.')[0]
        if symbol.endswith('.SH'):
            market_prefix = 'sh'
        else:
            market_prefix = 'sz'

        try:
            # Use Tencent K-line interface which includes price info
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

            change = float(latest['close']) - float(prev['close'])
            change_pct = (change / float(prev['close']) * 100) if float(prev['close']) != 0 else 0

            return {
                "symbol": symbol,
                "name": "",  # Will be filled from individual info if needed
                "price": float(latest['close']),
                "change": change,
                "change_pct": round(change_pct, 2),
                "volume": 0,
                "amount": float(latest['amount']),
                "high": float(latest['high']),
                "low": float(latest['low']),
                "open": float(latest['open']),
                "close": float(latest['close']),
                "timestamp": datetime.now().isoformat(),
            }
        except ValueError:
            raise
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
        """Get kline data for a symbol.

        Args:
            symbol: Stock code in format '000001.SZ' or '600000.SH'
            period: 'daily' or 'weekly'
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
        """
        _clear_proxy()

        # Strip suffix and determine market
        clean_symbol = symbol.split('.')[0]
        if symbol.endswith('.SH'):
            market_prefix = 'sh'
        else:
            market_prefix = 'sz'

        try:
            # Default dates
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

            return {
                "dates": [str(d) for d in df['date'].tolist()],
                "opens": [float(o) for o in df['open'].tolist()],
                "highs": [float(h) for h in df['high'].tolist()],
                "lows": [float(l) for l in df['low'].tolist()],
                "closes": [float(c) for c in df['close'].tolist()],
                "volumes": [float(v) for v in df['amount'].tolist()],
            }
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to get kline: {str(e)}")

    async def search(self, keyword: str) -> List[Dict[str, str]]:
        """Search stocks by keyword.

        Args:
            keyword: Search keyword (stock code or name)
        """
        _clear_proxy()

        try:
            # Get K-line data for the keyword as stock code
            clean_symbol = keyword.split('.')[0]
            if clean_symbol.isdigit() and len(clean_symbol) == 6:
                # Try as stock code
                market_prefix = 'sh' if clean_symbol.startswith(('6', '5')) else 'sz'
                df = ak.stock_zh_a_hist_tx(
                    symbol=f"{market_prefix}{clean_symbol}",
                    start_date="20260401",
                    end_date="20500101",
                    adjust="qfq"
                )
                if not df.empty:
                    market = 'SH' if clean_symbol.startswith(('6', '5')) else 'SZ'
                    return [{
                        "code": f"{clean_symbol}.{market}",
                        "name": "",
                        "market": market,
                        "type": "stock",
                    }]
            raise ValueError(f"No stock found for keyword: {keyword}")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to search: {str(e)}")
