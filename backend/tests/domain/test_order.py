import pytest
from app.domain.trading.aggregates.order import Order
from app.domain.trading.value_objects.order_side import OrderSideEnum
from app.domain.trading.value_objects.order_type import OrderTypeEnum
from app.domain.trading.value_objects.order_status import OrderStatusEnum
from app.domain.exceptions import InvalidOrderStateException


def test_order_cancel():
    """测试取消订单"""
    order = Order(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        side=OrderSideEnum.BUY,
        order_type=OrderTypeEnum.LIMIT,
        price=10.0,
        volume=100.0,
        status=OrderStatusEnum.PENDING,
    )

    order.cancel()
    assert order.status == OrderStatusEnum.CANCELLED


def test_order_fill_complete():
    """测试订单完全成交"""
    order = Order(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        side=OrderSideEnum.BUY,
        order_type=OrderTypeEnum.LIMIT,
        price=10.0,
        volume=100.0,
        status=OrderStatusEnum.PENDING,
    )

    order.fill(100.0, 10.0)
    assert order.status == OrderStatusEnum.FILLED
    assert order.filled_volume == 100.0


def test_order_fill_partial():
    """测试订单部分成交"""
    order = Order(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        side=OrderSideEnum.BUY,
        order_type=OrderTypeEnum.LIMIT,
        price=10.0,
        volume=100.0,
        status=OrderStatusEnum.PENDING,
    )

    order.fill(50.0, 10.0)
    assert order.status == OrderStatusEnum.PARTIAL
    assert order.filled_volume == 50.0
    assert order.remaining_volume == 50.0


def test_cancel_filled_order_raises():
    """测试取消已成交订单抛出异常"""
    order = Order(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        side=OrderSideEnum.BUY,
        order_type=OrderTypeEnum.LIMIT,
        price=10.0,
        volume=100.0,
        status=OrderStatusEnum.FILLED,
    )

    with pytest.raises(InvalidOrderStateException):
        order.cancel()


def test_remaining_volume():
    """测试剩余未成交数量"""
    order = Order(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        side=OrderSideEnum.BUY,
        order_type=OrderTypeEnum.LIMIT,
        price=10.0,
        volume=100.0,
        filled_volume=30.0,
        status=OrderStatusEnum.PARTIAL,
    )

    assert order.remaining_volume == 70.0


def test_is_fillable():
    """测试订单是否可成交"""
    order_pending = Order(
        id=1,
        user_id=1,
        symbol="000001.SZ",
        side=OrderSideEnum.BUY,
        order_type=OrderTypeEnum.LIMIT,
        price=10.0,
        volume=100.0,
        status=OrderStatusEnum.PENDING,
    )
    assert order_pending.is_fillable is True

    order_filled = Order(
        id=2,
        user_id=1,
        symbol="000001.SZ",
        side=OrderSideEnum.BUY,
        order_type=OrderTypeEnum.LIMIT,
        price=10.0,
        volume=100.0,
        status=OrderStatusEnum.FILLED,
    )
    assert order_filled.is_fillable is False
