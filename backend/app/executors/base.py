"""Base executor interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from app.models.order import Order
from app.models.position import Position


class BaseExecutor(ABC):
    """订单执行器基类"""

    @abstractmethod
    async def connect(self) -> bool:
        """连接交易终端

        Returns:
            连接是否成功
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        pass

    @abstractmethod
    async def place_order(self, order: Order) -> Dict[str, Any]:
        """下单

        Args:
            order: 订单对象

        Returns:
            订单结果字典，包含:
            - success: 是否成功
            - order_id: 订单ID（如果是实盘）
            - message: 消息
            - filled_price: 成交价格（如果是市价单）
            - filled_volume: 成交数量
        """
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """撤单

        Args:
            order_id: 订单ID

        Returns:
            是否成功
        """
        pass

    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """获取当前持仓

        Returns:
            持仓列表
        """
        pass

    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息

        Returns:
            账户信息字典，包含:
            - cash: 可用资金
            - total_assets: 总资产
            - positions_value: 持仓市值
            - market_value: 账户市值
        """
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """检查是否已连接

        Returns:
            是否已连接
        """
        pass
