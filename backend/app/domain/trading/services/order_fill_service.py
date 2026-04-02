from app.domain.trading.aggregates.order import Order
from app.domain.trading.aggregates.position import Position
from app.domain.trading.repositories.order_repository import OrderRepository
from app.domain.trading.repositories.position_repository import PositionRepository
from app.domain.exceptions import InvalidOrderStateException


class OrderFillService:
    """订单成交领域服务 - 处理订单成交和持仓更新的核心业务逻辑"""

    def __init__(
        self,
        order_repository: OrderRepository,
        position_repository: PositionRepository
    ):
        self.order_repository = order_repository
        self.position_repository = position_repository

    async def fill_order(
        self,
        order_id: int,
        filled_volume: float,
        filled_price: float
    ) -> Order:
        """执行订单成交"""
        order = await self.order_repository.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if not order.is_fillable:
            raise InvalidOrderStateException(
                f"Order {order_id} cannot be filled in status {order.status.value}"
            )

        # 更新订单状态
        order.fill(filled_volume, filled_price)
        await self.order_repository.save(order)

        # 更新持仓
        await self._update_position_on_fill(order, filled_volume, filled_price)

        return order

    async def _update_position_on_fill(
        self,
        order: Order,
        filled_volume: float,
        filled_price: float
    ) -> None:
        """根据成交更新持仓"""
        position = await self.position_repository.find_by_user_and_symbol(
            order.user_id,
            order.symbol
        )

        if order.side.value == "buy":
            # 买入：增加持仓
            if position:
                position.adjust_volume(filled_volume, filled_price)
            else:
                # 新建持仓
                position = Position(
                    user_id=order.user_id,
                    symbol=order.symbol,
                    volume=filled_volume,
                    frozen_volume=0.0,
                    avg_cost=filled_price,
                    current_price=filled_price,
                    mode=order.mode
                )
            await self.position_repository.save(position)

        elif order.side.value == "sell":
            # 卖出：减少持仓
            if position:
                position.adjust_volume(-filled_volume, filled_price)
                await self.position_repository.save(position)

    async def cancel_order(self, order_id: int) -> Order:
        """取消订单"""
        order = await self.order_repository.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.cancel()
        await self.order_repository.save(order)
        return order
