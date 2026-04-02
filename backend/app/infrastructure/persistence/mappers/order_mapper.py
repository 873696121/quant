from domain.trading.aggregates.order import Order
from domain.trading.value_objects.order_side import OrderSideEnum
from domain.trading.value_objects.order_type import OrderTypeEnum
from domain.trading.value_objects.order_status import OrderStatusEnum


def orm_to_order(orm_order) -> Order:
    """ORM模型转换为领域对象"""
    if orm_order is None:
        return None
    return Order(
        id=orm_order.id,
        user_id=orm_order.user_id,
        symbol=orm_order.symbol,
        side=OrderSideEnum(orm_order.direction.value),
        order_type=OrderTypeEnum(orm_order.order_type.value),
        price=float(orm_order.price) if orm_order.price else 0.0,
        stop_price=0.0,
        volume=orm_order.volume,
        filled_volume=orm_order.filled_volume,
        filled_price=0.0,
        status=OrderStatusEnum(orm_order.status.value),
        mode=orm_order.mode.value,
        backtest_id=orm_order.backtest_id,
        created_at=orm_order.created_at,
        updated_at=orm_order.updated_at,
    )


def order_to_orm(order: Order, orm_order) -> None:
    """领域对象映射到ORM模型"""
    orm_order.user_id = order.user_id
    orm_order.symbol = order.symbol
    orm_order.direction = order.side.value
    orm_order.order_type = order.order_type.value
    orm_order.price = order.price
    orm_order.stop_price = order.stop_price
    orm_order.volume = order.volume
    orm_order.filled_volume = order.filled_volume
    orm_order.status = order.status.value
    orm_order.mode = order.mode.value
    orm_order.backtest_id = order.backtest_id
