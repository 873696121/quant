from typing import Optional, List
from domain.trading.aggregates.position import Position


class PositionRepository:
    """持仓仓储接口（领域层定义）"""

    async def find_by_id(self, position_id: int) -> Optional[Position]:
        raise NotImplementedError

    async def find_by_user_id(self, user_id: int) -> List[Position]:
        raise NotImplementedError

    async def find_by_user_and_symbol(
        self,
        user_id: int,
        symbol: str
    ) -> Optional[Position]:
        raise NotImplementedError

    async def save(self, position: Position) -> Position:
        raise NotImplementedError

    async def delete(self, position_id: int) -> None:
        raise NotImplementedError
