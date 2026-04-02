import pytest
from app.domain.trading.aggregates.position import Position
from app.domain.trading.value_objects.position_mode import PositionModeEnum
from app.domain.exceptions import InsufficientPositionException


def test_position_buy_increase():
    """测试买入增加持仓"""
    position = Position(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        volume=100.0,
        frozen_volume=0.0,
        avg_cost=10.0,
        current_price=10.0,
    )

    position.adjust_volume(50.0, 11.0)

    assert position.volume == 150.0
    # 新平均成本 = (100*10 + 50*11) / 150 = 10.333...
    assert abs(position.avg_cost - 10.333) < 0.001


def test_position_sell_decrease():
    """测试卖出减少持仓"""
    position = Position(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        volume=100.0,
        frozen_volume=0.0,
        avg_cost=10.0,
        current_price=12.0,
    )

    position.adjust_volume(-30.0, 12.0)

    assert position.volume == 70.0
    assert position.avg_cost == 10.0  # 卖出不影响成本


def test_position_freeze():
    """测试冻结持仓"""
    position = Position(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        volume=100.0,
        frozen_volume=0.0,
        avg_cost=10.0,
        current_price=10.0,
    )

    position.freeze(30.0)
    assert position.frozen_volume == 30.0
    assert position.available_volume == 70.0


def test_position_freeze_insufficient():
    """测试冻结不足持仓"""
    position = Position(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        volume=100.0,
        frozen_volume=50.0,
        avg_cost=10.0,
        current_price=10.0,
    )

    with pytest.raises(InsufficientPositionException):
        position.freeze(60.0)  # 只有 50 可用


def test_position_unrealized_pnl():
    """测试浮动盈亏计算"""
    position = Position(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        volume=100.0,
        frozen_volume=0.0,
        avg_cost=10.0,
        current_price=12.0,
    )

    assert position.unrealized_pnl == 200.0  # (12-10)*100


def test_position_market_value():
    """测试市值计算"""
    position = Position(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        volume=100.0,
        frozen_volume=0.0,
        avg_cost=10.0,
        current_price=12.0,
    )

    assert position.market_value == 1200.0  # 12*100


def test_position_available_volume():
    """测试可用持仓数量"""
    position = Position(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        volume=100.0,
        frozen_volume=30.0,
        avg_cost=10.0,
        current_price=10.0,
    )

    assert position.available_volume == 70.0


def test_position_update_price():
    """测试更新当前价格"""
    position = Position(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        volume=100.0,
        frozen_volume=0.0,
        avg_cost=10.0,
        current_price=10.0,
    )

    position.update_price(12.0)
    assert position.current_price == 12.0
    assert position.unrealized_pnl == 200.0
