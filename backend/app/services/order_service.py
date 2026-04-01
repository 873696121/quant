"""Order management service with simulated fill."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus, OrderDirection
from app.models.position import Position
from app.schemas.order import OrderCreate


class OrderService:
    """Service for order operations with simulated fill."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_orders(
        self, user_id: int, mode: Optional[str] = None, status: Optional[str] = None
    ) -> List[Order]:
        """List orders for a user."""
        query = select(Order).where(Order.user_id == user_id)
        if mode:
            query = query.where(Order.mode == mode)
        if status:
            query = query.where(Order.status == status)
        query = query.order_by(Order.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, order_id: int, user_id: int) -> Optional[Order]:
        """Get an order by ID."""
        result = await self.db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_order(
        self, user_id: int, data: OrderCreate
    ) -> Order:
        """Create a new order and simulate fill."""
        # Create order
        order = Order(
            user_id=user_id,
            symbol=data.symbol,
            direction=data.direction,
            order_type=data.order_type,
            price=data.price,
            volume=data.volume,
            mode=data.mode,
            status=OrderStatus.PENDING,
        )
        self.db.add(order)
        await self.db.flush()

        # Simulate fill immediately
        order = await self._simulate_fill(order)
        return order

    async def _simulate_fill(self, order: Order) -> Order:
        """Simulate order fill and update position."""
        from decimal import Decimal

        # Mark as submitted then filled
        order.status = OrderStatus.SUBMITTED
        await self.db.flush()

        order.status = OrderStatus.FILLED
        order.filled_volume = order.volume
        await self.db.flush()

        # Update position
        if order.direction == OrderDirection.BUY:
            await self._update_position_buy(order)
        else:
            await self._update_position_sell(order)

        await self.db.refresh(order)
        return order

    async def _update_position_buy(self, order: Order) -> None:
        """Update position for buy order."""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == order.user_id,
                Position.symbol == order.symbol,
                Position.mode == order.mode,
            )
        )
        position = result.scalar_one_or_none()

        price = order.price or Decimal("0")
        if position:
            # Update existing position
            total_cost = position.avg_cost * position.volume + price * order.volume
            new_volume = position.volume + order.volume
            position.avg_cost = total_cost / new_volume if new_volume > 0 else Decimal("0")
            position.volume = new_volume
        else:
            # Create new position
            position = Position(
                user_id=order.user_id,
                symbol=order.symbol,
                volume=order.volume,
                avg_cost=price,
                mode=order.mode,
            )
            self.db.add(position)

        await self.db.flush()

    async def _update_position_sell(self, order: Order) -> None:
        """Update position for sell order."""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == order.user_id,
                Position.symbol == order.symbol,
                Position.mode == order.mode,
            )
        )
        position = result.scalar_one_or_none()

        if position:
            position.volume = max(0, position.volume - order.volume)
            await self.db.flush()

    async def cancel_order(self, order_id: int, user_id: int) -> bool:
        """Cancel an order (only pending orders)."""
        order = await self.get_by_id(order_id, user_id)
        if not order:
            return False

        if order.status != OrderStatus.PENDING:
            return False

        order.status = OrderStatus.CANCELLED
        await self.db.flush()
        return True
