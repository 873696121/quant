"""Dashboard data aggregation service."""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.position import Position
from app.models.strategy import Strategy


class DashboardService:
    """Service for dashboard data aggregation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self, user_id: int) -> Dict[str, Any]:
        """Get dashboard summary for a user."""
        # Get position count
        pos_result = await self.db.execute(
            select(func.count(Position.id)).where(Position.user_id == user_id)
        )
        position_count = pos_result.scalar() or 0

        # Get strategy count
        strat_result = await self.db.execute(
            select(func.count(Strategy.id)).where(Strategy.user_id == user_id)
        )
        strategy_count = strat_result.scalar() or 0

        # Get today's order count
        from datetime import datetime, date
        today = date.today()
        order_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.user_id == user_id,
                func.date(Order.created_at) == today,
            )
        )
        order_count = order_result.scalar() or 0

        # Calculate total asset (simplified - sum of position values + cash)
        # For now, return mock data as we don't have cash tracking
        total_asset = 100000.0  # Mock initial cash
        today_profit = 0.0

        return {
            "total_asset": total_asset,
            "today_profit": today_profit,
            "position_count": position_count,
            "strategy_count": strategy_count,
            "order_count": order_count,
        }

    async def get_positions(self, user_id: int, mode: str = "paper") -> List[Dict[str, Any]]:
        """Get positions for a user."""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.mode == mode,
            )
        )
        positions = result.scalars().all()

        return [
            {
                "id": p.id,
                "symbol": p.symbol,
                "volume": p.volume,
                "avg_cost": float(p.avg_cost),
                "frozen_volume": p.frozen_volume,
                "mode": p.mode,
                "current_price": None,
                "profit_loss": None,
            }
            for p in positions
        ]
