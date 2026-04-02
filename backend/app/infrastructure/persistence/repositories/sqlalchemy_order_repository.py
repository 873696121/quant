from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.trading.aggregates.order import Order
from app.domain.trading.repositories.order_repository import OrderRepository
from app.domain.trading.value_objects.order_status import OrderStatusEnum
from app.infrastructure.persistence.mappers.order_mapper import orm_to_order, order_to_orm
from app.models.order import Order as OrderModel


class SQLAlchemyOrderRepository(OrderRepository):
    """OrderRepository SQLAlchemy 实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, order_id: int) -> Optional[Order]:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        orm_order = result.scalar_one_or_none()
        return orm_to_order(orm_order)

    async def find_by_user_id(
        self,
        user_id: int,
        status: Optional[OrderStatusEnum] = None,
        limit: int = 100
    ) -> List[Order]:
        query = select(OrderModel).where(OrderModel.user_id == user_id)
        if status:
            query = query.where(OrderModel.status == status.value)
        query = query.limit(limit).order_by(OrderModel.id.desc())

        result = await self.session.execute(query)
        orm_orders = result.scalars().all()
        return [orm_to_order(o) for o in orm_orders]

    async def find_by_symbol(
        self,
        user_id: int,
        symbol: str,
        status: Optional[OrderStatusEnum] = None
    ) -> List[Order]:
        query = select(OrderModel).where(
            OrderModel.user_id == user_id,
            OrderModel.symbol == symbol
        )
        if status:
            query = query.where(OrderModel.status == status.value)

        result = await self.session.execute(query)
        orm_orders = result.scalars().all()
        return [orm_to_order(o) for o in orm_orders]

    async def save(self, order: Order) -> Order:
        if order.id is None:
            # 新增
            orm_order = OrderModel()
            order_to_orm(order, orm_order)
            self.session.add(orm_order)
            await self.session.flush()
            await self.session.refresh(orm_order)
            order.id = orm_order.id
        else:
            # 更新
            stmt = update(OrderModel).where(OrderModel.id == order.id).values(
                symbol=order.symbol,
                direction=order.side.value,
                order_type=order.order_type.value,
                price=order.price,
                stop_price=order.stop_price,
                volume=order.volume,
                filled_volume=order.filled_volume,
                status=order.status.value,
                mode=order.mode.value,
                backtest_id=order.backtest_id,
            )
            await self.session.execute(stmt)
        await self.session.commit()
        return order

    async def delete(self, order_id: int) -> None:
        await self.session.execute(
            delete(OrderModel).where(OrderModel.id == order_id)
        )
        await self.session.commit()
