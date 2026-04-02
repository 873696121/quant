from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from app.domain.strategy.value_objects.strategy_mode import StrategyModeEnum, BacktestStatusEnum


@dataclass
class Strategy:
    """策略聚合根"""
    id: Optional[int] = None
    user_id: int = 0
    name: str = ""
    code: str = ""
    mode: StrategyModeEnum = StrategyModeEnum.BACKTEST
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def update_config(self, config: Dict[str, Any]) -> None:
        """更新策略配置"""
        self.config = config
        self.updated_at = datetime.now()

    def update_code(self, code: str) -> None:
        """更新策略代码"""
        self.code = code
        self.updated_at = datetime.now()


@dataclass
class Backtest:
    """回测聚合根"""
    id: Optional[int] = None
    strategy_id: int = 0
    start_date: str = ""
    end_date: str = ""
    initial_cash: float = 0.0
    result_json: Dict[str, Any] = field(default_factory=dict)
    status: BacktestStatusEnum = BacktestStatusEnum.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def start(self) -> None:
        """开始回测"""
        self.status = BacktestStatusEnum.RUNNING
        self.updated_at = datetime.now()

    def complete(self, result: Dict[str, Any]) -> None:
        """完成回测"""
        self.result_json = result
        self.status = BacktestStatusEnum.COMPLETED
        self.updated_at = datetime.now()

    def fail(self, error: str) -> None:
        """回测失败"""
        self.result_json = {"error": error}
        self.status = BacktestStatusEnum.FAILED
        self.updated_at = datetime.now()
