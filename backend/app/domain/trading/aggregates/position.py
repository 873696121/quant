from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

from domain.exceptions import InsufficientPositionException
from domain.trading.value_objects.position_mode import PositionModeEnum


@dataclass
class Position:
    """持仓聚合根"""
    id: Optional[int] = None
    user_id: int = 0
    symbol: str = ""
    volume: float = 0.0
    frozen_volume: float = 0.0
    avg_cost: float = 0.0
    current_price: float = 0.0
    mode: PositionModeEnum = PositionModeEnum.BACKTEST
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def available_volume(self) -> float:
        """可用持仓数量"""
        return self.volume - self.frozen_volume

    @property
    def market_value(self) -> float:
        """市值"""
        return self.volume * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        """浮动盈亏"""
        return (self.current_price - self.avg_cost) * self.volume

    def freeze(self, volume: float) -> None:
        """冻结持仓"""
        if volume > self.available_volume:
            raise InsufficientPositionException(
                f"Insufficient position: required {volume}, available {self.available_volume}"
            )
        self.frozen_volume += volume
        self.updated_at = datetime.now()

    def unfreeze(self, volume: float) -> None:
        """解冻持仓"""
        if volume > self.frozen_volume:
            volume = self.frozen_volume
        self.frozen_volume -= volume
        self.updated_at = datetime.now()

    def update_price(self, new_price: float) -> None:
        """更新当前价格"""
        self.current_price = new_price
        self.updated_at = datetime.now()

    def adjust_volume(self, volume_delta: float, new_avg_cost: float) -> None:
        """调整持仓（买入增加或卖出减少）"""
        if volume_delta > 0:
            # 买入：增加持仓
            total_cost = self.avg_cost * self.volume + new_avg_cost * volume_delta
            self.volume += volume_delta
            self.avg_cost = total_cost / self.volume if self.volume > 0 else 0.0
        elif volume_delta < 0:
            # 卖出：减少持仓
            sold_volume = abs(volume_delta)
            if sold_volume > self.available_volume:
                raise InsufficientPositionException(
                    f"Insufficient available position: {self.available_volume}"
                )
            self.volume += volume_delta  # volume_delta 是负数
        self.updated_at = datetime.now()
