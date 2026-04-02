from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

from domain.exceptions import InvalidOrderStateException
from domain.trading.value_objects.order_side import OrderSideEnum
from domain.trading.value_objects.order_type import OrderTypeEnum
from domain.trading.value_objects.order_status import OrderStatusEnum


class OrderModeEnum(str, Enum):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


@dataclass
class Order:
    """订单聚合根"""
    id: Optional[int] = None
    user_id: int = 0
    symbol: str = ""
    side: OrderSideEnum = OrderSideEnum.BUY
    order_type: OrderTypeEnum = OrderTypeEnum.LIMIT
    price: float = 0.0
    stop_price: float = 0.0
    volume: float = 0.0
    filled_volume: float = 0.0
    filled_price: float = 0.0
    status: OrderStatusEnum = OrderStatusEnum.PENDING
    mode: OrderModeEnum = OrderModeEnum.BACKTEST
    backtest_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def cancel(self) -> None:
        """取消订单"""
        if self.status not in (OrderStatusEnum.PENDING, OrderStatusEnum.PARTIAL):
            raise InvalidOrderStateException(
                f"Cannot cancel order in status {self.status.value}"
            )
        self.status = OrderStatusEnum.CANCELLED
        self.updated_at = datetime.now()

    def fill(self, fill_volume: float, fill_price: float) -> None:
        """成交订单"""
        if self.status == OrderStatusEnum.FILLED:
            raise InvalidOrderStateException("Order already filled")
        if self.status == OrderStatusEnum.CANCELLED:
            raise InvalidOrderStateException("Cannot fill cancelled order")

        self.filled_volume += fill_volume
        self.filled_price = fill_price

        if self.filled_volume >= self.volume:
            self.status = OrderStatusEnum.FILLED
        else:
            self.status = OrderStatusEnum.PARTIAL
        self.updated_at = datetime.now()

    def reject(self) -> None:
        """拒绝订单"""
        if self.status != OrderStatusEnum.PENDING:
            raise InvalidOrderStateException(
                f"Cannot reject order in status {self.status.value}"
            )
        self.status = OrderStatusEnum.REJECTED
        self.updated_at = datetime.now()

    @property
    def remaining_volume(self) -> float:
        """剩余未成交数量"""
        return self.volume - self.filled_volume

    @property
    def is_fillable(self) -> bool:
        """是否可成交"""
        return self.status in (OrderStatusEnum.PENDING, OrderStatusEnum.PARTIAL)
