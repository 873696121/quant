"""Strategy management service."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategy import Strategy
from app.schemas.strategy import StrategyCreate, StrategyUpdate


class StrategyService:
    """Service for strategy operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(self, user_id: int) -> List[Strategy]:
        """List all strategies for a user."""
        result = await self.db.execute(
            select(Strategy)
            .where(Strategy.user_id == user_id)
            .order_by(Strategy.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, strategy_id: int, user_id: int) -> Optional[Strategy]:
        """Get a strategy by ID."""
        result = await self.db.execute(
            select(Strategy)
            .where(Strategy.id == strategy_id, Strategy.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, data: StrategyCreate) -> Strategy:
        """Create a new strategy."""
        strategy = Strategy(
            user_id=user_id,
            name=data.name,
            description=data.description,
            code=data.code,
            mode=data.mode,
            config=data.config,
        )
        self.db.add(strategy)
        await self.db.flush()
        await self.db.refresh(strategy)
        return strategy

    async def update(
        self, strategy_id: int, user_id: int, data: StrategyUpdate
    ) -> Optional[Strategy]:
        """Update a strategy."""
        strategy = await self.get_by_id(strategy_id, user_id)
        if not strategy:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(strategy, key, value)

        await self.db.flush()
        await self.db.refresh(strategy)
        return strategy

    async def delete(self, strategy_id: int, user_id: int) -> bool:
        """Delete a strategy."""
        strategy = await self.get_by_id(strategy_id, user_id)
        if not strategy:
            return False

        await self.db.delete(strategy)
        await self.db.flush()
        return True
