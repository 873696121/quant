"""Built-in trading strategies."""

from typing import Dict, Any
import pandas as pd


class BaseStrategy:
    """策略基类"""

    name: str = "BaseStrategy"
    params: Dict[str, Any] = {}

    def __init__(self, params: Dict[str, Any] = None):
        if params:
            self.params.update(params)

    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号

        Args:
            market_data: K线数据，包含 open, high, low, close, volume

        Returns:
            DataFrame，包含 signal 列: 1买入, -1卖出, 0观望
        """
        raise NotImplementedError


class MeanReversionStrategy(BaseStrategy):
    """均线回归策略

    当价格偏离均线过多时，预期会回归
    """

    name = "MeanReversion"

    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            "window": 20,      # 均线周期
            "threshold": 0.02, # 偏离阈值 2%
        }
        super().__init__(default_params)
        if params:
            self.params.update(params)

    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        window = self.params["window"]
        threshold = self.params["threshold"]

        if len(market_data) < window:
            return pd.DataFrame()

        df = market_data.copy()
        df["ma"] = df["close"].rolling(window=window).mean()
        df["deviation"] = (df["close"] - df["ma"]) / df["ma"]

        df["signal"] = 0
        df.loc[df["deviation"] < -threshold, "signal"] = 1   # 价格低于均线，买入
        df.loc[df["deviation"] > threshold, "signal"] = -1  # 价格高于均线，卖出

        # 返回最新信号
        signals = df[df["signal"] != 0][["close"]].tail(10)
        result = []
        for idx, row in signals.iterrows():
            result.append({
                "symbol": market_data.get("symbol", "000001"),
                "price": row["close"],
                "volume": 100,
                "action": "buy" if df.loc[idx, "signal"] == 1 else "sell"
            })
        return pd.DataFrame(result)


class MomentumStrategy(BaseStrategy):
    """动量策略

    追涨杀跌：价格向上突破时买入，向下突破时卖出
    """

    name = "Momentum"

    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            "short_window": 5,   # 短期均线
            "long_window": 20,   # 长期均线
        }
        super().__init__(default_params)
        if params:
            self.params.update(params)

    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        short = self.params["short_window"]
        long = self.params["long_window"]

        if len(market_data) < long:
            return pd.DataFrame()

        df = market_data.copy()
        df["short_ma"] = df["close"].rolling(window=short).mean()
        df["long_ma"] = df["close"].rolling(window=long).mean()

        df["signal"] = 0
        df.loc[
            (df["short_ma"] > df["long_ma"]) &
            (df["short_ma"].shift(1) <= df["long_ma"].shift(1)),
            "signal"
        ] = 1   # 金叉，买入
        df.loc[
            (df["short_ma"] < df["long_ma"]) &
            (df["short_ma"].shift(1) >= df["long_ma"].shift(1)),
            "signal"
        ] = -1  # 死叉，卖出

        signals = df[df["signal"] != 0][["close"]].tail(10)
        result = []
        for idx, row in signals.iterrows():
            result.append({
                "symbol": market_data.get("symbol", "000001"),
                "price": row["close"],
                "volume": 100,
                "action": "buy" if df.loc[idx, "signal"] == 1 else "sell"
            })
        return pd.DataFrame(result)


class BreakoutStrategy(BaseStrategy):
    """突破策略

    当价格突破历史高点时买入，突破历史低点时卖出
    """

    name = "Breakout"

    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            "window": 20,  # 窗口期
            "volume_threshold": 1.5,  # 成交量倍数
        }
        super().__init__(default_params)
        if params:
            self.params.update(params)

    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        window = self.params["window"]

        if len(market_data) < window:
            return pd.DataFrame()

        df = market_data.copy()
        df["highest"] = df["high"].rolling(window=window).max().shift(1)
        df["lowest"] = df["low"].rolling(window=window).min().shift(1)

        df["signal"] = 0
        df.loc[df["close"] > df["highest"], "signal"] = 1   # 突破高点，买入
        df.loc[df["close"] < df["lowest"], "signal"] = -1   # 突破低点，卖出

        signals = df[df["signal"] != 0][["close"]].tail(10)
        result = []
        for idx, row in signals.iterrows():
            result.append({
                "symbol": market_data.get("symbol", "000001"),
                "price": row["close"],
                "volume": 100,
                "action": "buy" if df.loc[idx, "signal"] == 1 else "sell"
            })
        return pd.DataFrame(result)
