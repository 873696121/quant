from domain.trading.aggregates.position import Position
from domain.trading.value_objects.position_mode import PositionModeEnum


def orm_to_position(orm_position) -> Position:
    """ORM模型转换为领域对象"""
    if orm_position is None:
        return None
    return Position(
        id=orm_position.id,
        user_id=orm_position.user_id,
        symbol=orm_position.symbol,
        volume=orm_position.volume,
        frozen_volume=orm_position.frozen_volume,
        avg_cost=float(orm_position.avg_cost) if orm_position.avg_cost else 0.0,
        current_price=float(orm_position.current_price) if orm_position.current_price else 0.0,
        mode=PositionModeEnum(orm_position.mode.value),
        created_at=orm_position.created_at,
        updated_at=orm_position.updated_at,
    )


def position_to_orm(position: Position, orm_position) -> None:
    """领域对象映射到ORM模型"""
    orm_position.user_id = position.user_id
    orm_position.symbol = position.symbol
    orm_position.volume = position.volume
    orm_position.frozen_volume = position.frozen_volume
    orm_position.avg_cost = position.avg_cost
    orm_position.current_price = position.current_price
    orm_position.mode = position.mode.value
