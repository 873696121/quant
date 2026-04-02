from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.trading.aggregates.position import Position
from domain.trading.repositories.position_repository import PositionRepository
from infrastructure.persistence.mappers.position_mapper import orm_to_position, position_to_orm
from models.position import Position as PositionModel


class SQLAlchemyPositionRepository(PositionRepository):
    """PositionRepository SQLAlchemy 实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, position_id: int) -> Optional[Position]:
        result = await self.session.execute(
            select(PositionModel).where(PositionModel.id == position_id)
        )
        orm_position = result.scalar_one_or_none()
        return orm_to_position(orm_position)

    async def find_by_user_id(self, user_id: int) -> List[Position]:
        result = await self.session.execute(
            select(PositionModel).where(PositionModel.user_id == user_id)
        )
        orm_positions = result.scalars().all()
        return [orm_to_position(p) for p in orm_positions]

    async def find_by_user_and_symbol(
        self,
        user_id: int,
        symbol: str
    ) -> Optional[Position]:
        result = await self.session.execute(
            select(PositionModel).where(
                PositionModel.user_id == user_id,
                PositionModel.symbol == symbol
            )
        )
        orm_position = result.scalar_one_or_none()
        return orm_to_position(orm_position)

    async def save(self, position: Position) -> Position:
        if position.id is None:
            orm_position = PositionModel()
            position_to_orm(position, orm_position)
            self.session.add(orm_position)
            await self.session.flush()
            await self.session.refresh(orm_position)
            position.id = orm_position.id
        else:
            stmt = update(PositionModel).where(PositionModel.id == position.id).values(
                symbol=position.symbol,
                volume=position.volume,
                frozen_volume=position.frozen_volume,
                avg_cost=position.avg_cost,
                current_price=position.current_price,
                mode=position.mode.value,
            )
            await self.session.execute(stmt)
        await self.session.commit()
        return position

    async def delete(self, position_id: int) -> None:
        await self.session.execute(
            delete(PositionModel).where(PositionModel.id == position_id)
        )
        await self.session.commit()
