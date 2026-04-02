from enum import Enum


class OrderSideEnum(str, Enum):
    """订单方向枚举"""
    BUY = "buy"
    SELL = "sell"
