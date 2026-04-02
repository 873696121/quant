from enum import Enum


class PositionModeEnum(str, Enum):
    """持仓模式枚举"""
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"
