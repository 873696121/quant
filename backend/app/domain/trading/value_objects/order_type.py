from enum import Enum


class OrderTypeEnum(str, Enum):
    """订单类型枚举"""
    LIMIT = "limit"
    MARKET = "market"
    STOP = "stop"
