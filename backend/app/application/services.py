"""Application layer service factory.

Provides dependency injection for DDD application services.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.infrastructure.persistence.repositories.sqlalchemy_order_repository import (
    SQLAlchemyOrderRepository
)
from app.infrastructure.persistence.repositories.sqlalchemy_position_repository import (
    SQLAlchemyPositionRepository
)
from app.domain.trading.services.order_fill_service import OrderFillService
from app.application.trading.commands.handlers import OrderCommandHandler


def get_order_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> SQLAlchemyOrderRepository:
    return SQLAlchemyOrderRepository(session)


def get_position_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> SQLAlchemyPositionRepository:
    return SQLAlchemyPositionRepository(session)


def get_order_fill_service(
    order_repo: Annotated[SQLAlchemyOrderRepository, Depends(get_order_repository)],
    position_repo: Annotated[SQLAlchemyPositionRepository, Depends(get_position_repository)]
) -> OrderFillService:
    return OrderFillService(order_repo, position_repo)


def get_order_command_handler(
    order_repo: Annotated[SQLAlchemyOrderRepository, Depends(get_order_repository)],
    fill_service: Annotated[OrderFillService, Depends(get_order_fill_service)]
) -> OrderCommandHandler:
    return OrderCommandHandler(order_repo, fill_service)
