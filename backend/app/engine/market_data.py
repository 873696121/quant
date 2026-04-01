"""Market data provider using akshare."""

from typing import Optional, List
import pandas as pd


class MarketDataProvider:
    """市场数据提供者

    从 akshare 获取 A 股市场数据
    """

    def __init__(self):
        self._ak = None
        self._try_import_akshare()

    def _try_import_akshare(self):
        """尝试导入 akshare"""
        try:
            import akshare as ak
            self._ak = ak
        except ImportError:
            print("Warning: akshare not installed, market data will be simulated")

    async def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str = "daily",
    ) -> pd.DataFrame:
        """获取历史K线数据

        Args:
            symbol: 股票代码，如 "000001"（平安银行）
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            period: K线周期 daily/weekly/monthly

        Returns:
            DataFrame，包含 open, high, low, close, volume 列
        """
        if not self._ak:
            return self._generate_mock_data(symbol, start_date, end_date)

        try:
            if period == "daily":
                df = self._ak.stock_zh_a_hist(
                    symbol=symbol,
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust="qfq"
                )
            elif period == "weekly":
                df = self._ak.stock_zh_a_hist(
                    symbol=symbol,
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust="qfq",
                    period="weekly"
                )
            else:
                df = self._ak.stock_zh_a_hist(
                    symbol=symbol,
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust="qfq"
                )

            # 重命名列
            df = df.rename(columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "涨跌幅": "pct_change"
            })

            df["symbol"] = symbol
            return df

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return self._generate_mock_data(symbol, start_date, end_date)

    async def get_realtime_data(self, symbol: str) -> dict:
        """获取实时行情

        Args:
            symbol: 股票代码

        Returns:
            行情字典
        """
        if not self._ak:
            return self._generate_mock_realtime(symbol)

        try:
            df = self._ak.stock_zh_a_spot_em()
            row = df[df["代码"] == symbol]
            if row.empty:
                return self._generate_mock_realtime(symbol)

            return {
                "symbol": symbol,
                "name": row["名称"].values[0],
                "price": float(row["最新价"].values[0]),
                "change": float(row["涨跌幅"].values[0]),
                "volume": float(row["成交量"].values[0]),
                "amount": float(row["成交额"].values[0]),
                "high": float(row["最高"].values[0]),
                "low": float(row["最低"].values[0]),
                "open": float(row["今开"].values[0]),
                "prev_close": float(row["昨收"].values[0]),
            }
        except Exception as e:
            print(f"Error fetching realtime for {symbol}: {e}")
            return self._generate_mock_realtime(symbol)

    async def get_realtime_quotes(self, symbols: List[str]) -> List[dict]:
        """批量获取实时行情

        Args:
            symbols: 股票代码列表

        Returns:
            行情列表
        """
        results = []
        for symbol in symbols:
            data = await self.get_realtime_data(symbol)
            results.append(data)
        return results

    def _generate_mock_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """生成模拟数据用于测试"""
        from datetime import datetime, timedelta

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        dates = []
        current = start
        while current <= end:
            if current.weekday() < 5:  # 工作日
                dates.append(current)
            current += timedelta(days=1)

        import numpy as np

        n = len(dates)
        base_price = 10.0

        data = {
            "date": [d.strftime("%Y-%m-%d") for d in dates],
            "open": np.random.uniform(base_price * 0.98, base_price * 1.02, n),
            "close": np.random.uniform(base_price * 0.97, base_price * 1.03, n),
            "high": np.random.uniform(base_price * 1.00, base_price * 1.04, n),
            "low": np.random.uniform(base_price * 0.96, base_price * 1.00, n),
            "volume": np.random.randint(1000000, 10000000, n),
            "symbol": [symbol] * n,
        }

        df = pd.DataFrame(data)
        return df

    def _generate_mock_realtime(self, symbol: str) -> dict:
        """生成模拟实时行情"""
        import random
        return {
            "symbol": symbol,
            "name": f"股票{symbol}",
            "price": round(random.uniform(5, 50), 2),
            "change": round(random.uniform(-10, 10), 2),
            "volume": random.randint(1000000, 100000000),
            "amount": random.randint(10000000, 1000000000),
            "high": round(random.uniform(10, 50), 2),
            "low": round(random.uniform(5, 15), 2),
            "open": round(random.uniform(5, 50), 2),
            "prev_close": round(random.uniform(5, 50), 2),
        }
