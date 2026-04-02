from enum import Enum


class OrderStatusEnum(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"       # 待成交
    FILLED = "filled"         # 已成交
    PARTIAL = "partial"       # 部分成交
    CANCELLED = "cancelled"   # 已取消
    REJECTED = "rejected"     # 已拒绝
