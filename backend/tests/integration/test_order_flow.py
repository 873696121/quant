import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.infrastructure.persistence.repositories.sqlalchemy_order_repository import (
    SQLAlchemyOrderRepository
)
from app.domain.trading.aggregates.order import Order
from app.domain.trading.value_objects.order_side import OrderSideEnum
from app.domain.trading.value_objects.order_type import OrderTypeEnum


@pytest_asyncio.fixture
async def db_session():
    """创建测试数据库会话"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_order_crud_flow(db_session):
    """测试订单 CRUD 流程"""
    repo = SQLAlchemyOrderRepository(db_session)

    # 创建订单
    order = Order(
        user_id=1,
        symbol="000001.SZ",
        side=OrderSideEnum.BUY,
        order_type=OrderTypeEnum.LIMIT,
        price=10.0,
        volume=100.0,
    )

    saved_order = await repo.save(order)
    assert saved_order.id is not None

    # 查询订单
    found = await repo.find_by_id(saved_order.id)
    assert found is not None
    assert found.symbol == "000001.SZ"

    # 取消订单
    found.cancel()
    await repo.save(found)

    # 验证状态
    cancelled = await repo.find_by_id(saved_order.id)
    assert cancelled.status.value == "cancelled"


@pytest.mark.asyncio
async def test_order_fill_flow(db_session):
    """测试订单成交流程"""
    repo = SQLAlchemyOrderRepository(db_session)

    # 创建订单
    order = Order(
        user_id=1,
        symbol="000001.SZ",
        side=OrderSideEnum.BUY,
        order_type=OrderTypeEnum.LIMIT,
        price=10.0,
        volume=100.0,
    )

    saved_order = await repo.save(order)
    assert saved_order.status.value == "pending"

    # 直接成交全部
    saved_order.fill(100.0, 10.0)
    await repo.save(saved_order)

    # 验证完全成交
    filled = await repo.find_by_id(saved_order.id)
    assert filled.status.value == "filled"
    assert filled.filled_volume == 100.0
