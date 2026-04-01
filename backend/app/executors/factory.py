"""Executor factory."""

from typing import Dict, Any

from app.models.strategy import StrategyMode
from .base import BaseExecutor
from .simulated_executor import SimulatedExecutor
from .qmt_executor import QMTExecutor


def get_executor(mode: str, config: Dict[str, Any] = None) -> BaseExecutor:
    """根据模式返回执行器

    Args:
        mode: 执行模式
            - "backtest": 回测模式，使用 SimulatedExecutor
            - "paper": 模拟交易模式，使用 SimulatedExecutor
            - "live": 实盘交易模式，使用 QMTExecutor
        config: 执行器配置

    Returns:
        对应模式的执行器实例

    Raises:
        ValueError: 当模式不支持时
    """
    if mode == StrategyMode.BACKTEST or mode == "backtest":
        return SimulatedExecutor(
            initial_cash=config.get("initial_cash", 1000000)
            if config else 1000000
        )
    elif mode == StrategyMode.PAPER or mode == "paper":
        return SimulatedExecutor(
            initial_cash=config.get("initial_cash", 1000000)
            if config else 1000000
        )
    elif mode == StrategyMode.LIVE or mode == "live":
        if not config:
            raise ValueError("Live mode requires QMT config")
        return QMTExecutor(config)
    else:
        raise ValueError(f"Unknown execution mode: {mode}")
