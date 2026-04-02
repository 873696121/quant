from app.application.trading.commands.order_commands import CreateOrderCommand, CancelOrderCommand
from app.domain.trading.aggregates.order import Order
from app.domain.trading.services.order_fill_service import OrderFillService
from app.domain.trading.repositories.order_repository import OrderRepository


class OrderCommandHandler:
    """订单命令处理器"""

    def __init__(
        self,
        order_repository: OrderRepository,
        order_fill_service: OrderFillService
    ):
        self.order_repository = order_repository
        self.order_fill_service = order_fill_service

    async def handle_create_order(self, cmd: CreateOrderCommand) -> Order:
        """处理创建订单"""
        order = Order(
            user_id=cmd.user_id,
            symbol=cmd.symbol,
            side=cmd.side,
            order_type=cmd.order_type,
            price=cmd.price,
            volume=cmd.volume,
            mode=cmd.mode,
            stop_price=cmd.stop_price,
        )
        return await self.order_repository.save(order)

    async def handle_cancel_order(self, cmd: CancelOrderCommand) -> Order:
        """处理取消订单"""
        order = await self.order_repository.find_by_id(cmd.order_id)
        if order and order.user_id == cmd.user_id:
            return await self.order_fill_service.cancel_order(cmd.order_id)
        raise ValueError("Order not found or unauthorized")
