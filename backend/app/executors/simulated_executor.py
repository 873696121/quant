"""Simulated executor for backtest and paper trading."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List

from app.models.order import Order, OrderDirection, OrderType, OrderStatus, OrderMode
from app.models.position import Position, PositionMode
from .base import BaseExecutor


class SimulatedExecutor(BaseExecutor):
    """模拟执行器

    用于回测和 paper trading 模式
    - 回测: 历史数据，模拟成交
    - Paper: 实时数据，模拟成交
    """

    def __init__(self, initial_cash: float = 1000000.0):
        self.initial_cash = Decimal(str(initial_cash))
        self.cash = self.initial_cash
        self.positions: Dict[str, Dict] = {}  # symbol -> {volume, avg_cost}
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self.connected = False
        self._order_id_counter = 0

    async def connect(self) -> bool:
        """连接（模拟总是成功）"""
        self.connected = True
        return True

    async def disconnect(self) -> None:
        """断开连接"""
        self.connected = False

    async def is_connected(self) -> bool:
        return self.connected

    async def place_order(self, order: Order) -> Dict[str, Any]:
        """模拟下单

        市价单: 立即以模拟价格成交
        限价单: 检查价格条件后成交
        """
        if not self.connected:
            return {
                "success": False,
                "message": "执行器未连接",
                "order_id": None,
            }

        self._order_id_counter += 1
        order_id = f"sim_{self._order_id_counter}"

        # 模拟价格
        if order.order_type == OrderType.MARKET:
            # 市价单: 使用固定模拟价格
            filled_price = self._get_simulated_price(order.symbol, order.direction)
        else:
            # 限价单: 使用指定价格
            filled_price = order.price if order.price else Decimal("0")

        filled_price = Decimal(str(filled_price))

        # 检查资金/持仓是否足够
        if order.direction == OrderDirection.BUY:
            required = filled_price * order.volume
            commission = required * Decimal("0.0003")
            total_cost = required + commission

            if total_cost > self.cash:
                return {
                    "success": False,
                    "message": "资金不足",
                    "order_id": order_id,
                    "filled_price": None,
                    "filled_volume": 0,
                }

            # 成交
            self.cash -= total_cost

            # 更新持仓
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                total_vol = pos["volume"] + order.volume
                pos["avg_cost"] = (
                    pos["avg_cost"] * pos["volume"] + filled_price * order.volume
                ) / total_vol
                pos["volume"] = total_vol
            else:
                self.positions[order.symbol] = {
                    "volume": order.volume,
                    "avg_cost": filled_price,
                }

        else:  # SELL
            if order.symbol not in self.positions:
                return {
                    "success": False,
                    "message": "无持仓",
                    "order_id": order_id,
                    "filled_price": None,
                    "filled_volume": 0,
                }

            pos = self.positions[order.symbol]
            if order.volume > pos["volume"]:
                return {
                    "success": False,
                    "message": "持仓不足",
                    "order_id": order_id,
                    "filled_price": None,
                    "filled_volume": 0,
                }

            # 成交
            revenue = filled_price * order.volume
            stamp_tax = revenue * Decimal("0.001")  # 印花税
            commission = revenue * Decimal("0.0003")  # 佣金
            self.cash += revenue - stamp_tax - commission

            # 更新持仓
            pos["volume"] -= order.volume
            if pos["volume"] <= 0:
                del self.positions[order.symbol]

        # 记录订单
        order.id = self._order_id_counter
        order.status = OrderStatus.FILLED
        order.filled_volume = order.volume
        self.orders[order_id] = order

        return {
            "success": True,
            "message": "成交",
            "order_id": order_id,
            "filled_price": float(filled_price),
            "filled_volume": order.volume,
        }

    async def cancel_order(self, order_id: str) -> bool:
        """模拟撤单

        如果订单未成交，可以撤单
        """
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        if order.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
            order.status = OrderStatus.CANCELLED
            return True

        return False

    async def get_positions(self) -> List[Position]:
        """获取当前持仓"""
        positions = []
        for symbol, pos in self.positions.items():
            positions.append(
                Position(
                    symbol=symbol,
                    volume=pos["volume"],
                    avg_cost=Decimal(str(pos["avg_cost"])),
                    frozen_volume=0,
                    mode=PositionMode.PAPER,
                )
            )
        return positions

    async def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        positions_value = Decimal("0")
        for symbol, pos in self.positions.items():
            current_price = self._get_simulated_price(symbol, OrderDirection.BUY)
            positions_value += Decimal(str(current_price)) * pos["volume"]

        return {
            "cash": float(self.cash),
            "total_assets": float(self.cash + positions_value),
            "positions_value": float(positions_value),
            "available_cash": float(self.cash),
        }

    def _get_simulated_price(self, symbol: str, direction: OrderDirection) -> float:
        """获取模拟价格"""
        import random
        base = 10.0 + hash(symbol) % 100
        if direction == OrderDirection.BUY:
            return round(base * random.uniform(0.99, 1.01), 2)
        else:
            return round(base * random.uniform(0.99, 1.01), 2)

    def reset(self) -> None:
        """重置账户（用于回测）"""
        self.cash = self.initial_cash
        self.positions.clear()
        self.orders.clear()
        self._order_id_counter = 0
