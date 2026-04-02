from enum import Enum


class StrategyModeEnum(str, Enum):
    """策略模式枚举"""
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


class BacktestStatusEnum(str, Enum):
    """回测状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
