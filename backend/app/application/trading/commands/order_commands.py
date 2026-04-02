from dataclasses import dataclass
from app.domain.trading.value_objects.order_side import OrderSideEnum
from app.domain.trading.value_objects.order_type import OrderTypeEnum


@dataclass
class CreateOrderCommand:
    """创建订单命令"""
    user_id: int
    symbol: str
    side: OrderSideEnum
    order_type: OrderTypeEnum
    price: float
    volume: float
    mode: str = "backtest"
    stop_price: float = 0.0


@dataclass
class CancelOrderCommand:
    """取消订单命令"""
    order_id: int
    user_id: int
