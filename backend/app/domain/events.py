from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4


@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: str
    occurred_on: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "occurred_on": self.occurred_on.isoformat(),
            "event_type": self.__class__.__name__,
        }


@dataclass
class OrderFilledEvent(DomainEvent):
    """订单成交事件"""
    order_id: int
    user_id: int
    symbol: str
    side: str
    filled_volume: float
    filled_price: float

    def __post_init__(self):
        self.event_id = str(uuid4())
        self.occurred_on = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "order_id": self.order_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side,
            "filled_volume": self.filled_volume,
            "filled_price": self.filled_price,
        })
        return base


@dataclass
class OrderCancelledEvent(DomainEvent):
    """订单取消事件"""
    order_id: int
    user_id: int
    reason: str = ""

    def __post_init__(self):
        self.event_id = str(uuid4())
        self.occurred_on = datetime.now()
