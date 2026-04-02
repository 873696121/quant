from typing import Optional, List
from app.domain.trading.aggregates.order import Order
from app.domain.trading.value_objects.order_status import OrderStatusEnum


class OrderRepository:
    """订单仓储接口（领域层定义）"""

    async def find_by_id(self, order_id: int) -> Optional[Order]:
        raise NotImplementedError

    async def find_by_user_id(
        self,
        user_id: int,
        status: Optional[OrderStatusEnum] = None,
        limit: int = 100
    ) -> List[Order]:
        raise NotImplementedError

    async def find_by_symbol(
        self,
        user_id: int,
        symbol: str,
        status: Optional[OrderStatusEnum] = None
    ) -> List[Order]:
        raise NotImplementedError

    async def save(self, order: Order) -> Order:
        raise NotImplementedError

    async def delete(self, order_id: int) -> None:
        raise NotImplementedError
