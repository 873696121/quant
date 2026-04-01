"""QMT (MiniQMT) executor for live trading."""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional

from app.models.order import Order, OrderDirection, OrderType, OrderStatus, OrderMode
from app.models.position import Position, PositionMode
from .base import BaseExecutor


class QMTExecutor(BaseExecutor):
    """QMT (MiniQMT) 实盘执行器

    QMT API 参考:
    - 登录: xtstockophon/login
    - 下单: xtstockophon/place_order
    - 撤单: xtstockophon/cancel_order
    - 持仓: xtstockophon/get_positions / xtstockophon/query_stock_pool
    - 账户: xtstockophon/query_balance
    """

    def __init__(self, config: Dict[str, Any]):
        """初始化 QMT 执行器

        Args:
            config: QMT 配置，包含:
                - ip: QMT 服务器 IP，默认 127.0.0.1
                - port: QMT 端口，默认 8088
                - username: QMT 用户名
                - password: QMT 密码
                - account_id: 交易账号
        """
        self.config = config
        self.ip = config.get("ip", "127.0.0.1")
        self.port = config.get("port", 8088)
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.account_id = config.get("account_id", "")

        self.connected = False
        self._qmt_api = None
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """连接 QMT 终端"""
        if self.connected:
            return True

        try:
            loop = asyncio.get_event_loop()

            # 尝试在线程池中执行同步的 QMT API
            await loop.run_in_executor(
                None,
                self._sync_connect
            )

            self.connected = True
            return True

        except Exception as e:
            self.connected = False
            raise ConnectionError(f"QMT连接失败: {e}")

    def _sync_connect(self) -> None:
        """同步连接 QMT"""
        try:
            import xtstockophon

            # 调用 QMT 登录接口
            result = xtstockophon.login(
                self.ip,
                self.port,
                self.username,
                self.password,
            )

            if result != 0:
                raise ConnectionError(f"QMT login failed with code: {result}")

            self._qmt_api = xtstockophon
            self.connected = True

        except ImportError:
            raise ImportError(
                "QMT API (xtstockophon) not installed. "
                "Please install QMT Python API package."
            )

    async def disconnect(self) -> None:
        """断开 QMT 连接"""
        if not self.connected:
            return

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._sync_disconnect
            )
        except Exception:
            pass
        finally:
            self.connected = False
            self._qmt_api = None

    def _sync_disconnect(self) -> None:
        """同步断开连接"""
        if self._qmt_api:
            try:
                self._qmt_api.logout()
            except Exception:
                pass

    async def is_connected(self) -> bool:
        return self.connected

    async def place_order(self, order: Order) -> Dict[str, Any]:
        """下单到 QMT

        Args:
            order: 订单对象

        Returns:
            订单结果
        """
        if not self.connected:
            return {
                "success": False,
                "message": "QMT 未连接",
                "order_id": None,
            }

        async with self._lock:
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._sync_place_order,
                    order
                )
                return result

            except Exception as e:
                return {
                    "success": False,
                    "message": f"下单失败: {e}",
                    "order_id": None,
                }

    def _sync_place_order(self, order: Order) -> Dict[str, Any]:
        """同步下单"""
        if not self._qmt_api:
            return {
                "success": False,
                "message": "QMT API 未初始化",
                "order_id": None,
            }

        try:
            # 转换订单格式
            direction = 1 if order.direction == OrderDirection.BUY else 2
            order_type = 11 if order.order_type == OrderType.MARKET else 10

            # QMT 下单
            result = self._qmt_api.place_order(
                self.account_id,
                order.symbol,
                direction,
                order_type,
                float(order.price) if order.price else 0,
                order.volume,
            )

            if result is None or result == "":
                return {
                    "success": False,
                    "message": "下单返回为空",
                    "order_id": None,
                }

            # 解析返回
            # result 格式: "订单号,成功标志,成交价格,成交数量"
            parts = str(result).split(",")
            if len(parts) >= 4:
                order_id = parts[0]
                success = parts[1] == "1"
                filled_price = float(parts[2]) if parts[2] else 0
                filled_volume = int(parts[3]) if parts[3] else 0

                return {
                    "success": success,
                    "message": "成功" if success else "失败",
                    "order_id": order_id,
                    "filled_price": filled_price,
                    "filled_volume": filled_volume,
                }
            else:
                return {
                    "success": False,
                    "message": f"下单返回格式错误: {result}",
                    "order_id": None,
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"下单异常: {e}",
                "order_id": None,
            }

    async def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        if not self.connected:
            return False

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._sync_cancel_order,
                order_id
            )
            return result

        except Exception:
            return False

    def _sync_cancel_order(self, order_id: str) -> bool:
        """同步撤单"""
        if not self._qmt_api:
            return False

        try:
            result = self._qmt_api.cancel_order(self.account_id, order_id)
            return result == 1 or result == "1"
        except Exception:
            return False

    async def get_positions(self) -> List[Position]:
        """获取持仓"""
        if not self.connected:
            return []

        try:
            loop = asyncio.get_event_loop()
            positions_data = await loop.run_in_executor(
                None,
                self._sync_get_positions
            )
            return positions_data

        except Exception:
            return []

    def _sync_get_positions(self) -> List[Position]:
        """同步获取持仓"""
        if not self._qmt_api:
            return []

        try:
            # 获取持仓
            result = self._qmt_api.get_positions(self.account_id)
            if not result:
                return []

            positions = []
            # result 格式: "股票代码,持仓量,成本价,现价,..."
            for line in str(result).split(";"):
                if not line.strip():
                    continue

                parts = line.split(",")
                if len(parts) >= 4:
                    symbol = parts[0]
                    volume = int(parts[1])
                    avg_cost = Decimal(parts[2])
                    current_price = Decimal(parts[3])

                    positions.append(
                        Position(
                            symbol=symbol,
                            volume=volume,
                            avg_cost=avg_cost,
                            current_price=float(current_price),
                            frozen_volume=0,
                            mode=PositionMode.LIVE,
                        )
                    )

            return positions

        except Exception:
            return []

    async def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        if not self.connected:
            return {
                "cash": 0,
                "total_assets": 0,
                "positions_value": 0,
                "available_cash": 0,
            }

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._sync_get_account_info
            )
            return result

        except Exception:
            return {
                "cash": 0,
                "total_assets": 0,
                "positions_value": 0,
                "available_cash": 0,
            }

    def _sync_get_account_info(self) -> Dict[str, Any]:
        """同步获取账户信息"""
        if not self._qmt_api:
            return {}

        try:
            result = self._qmt_api.query_balance(self.account_id)
            if not result:
                return {}

            # result 格式: "可用资金,总资产,持仓市值,..."
            parts = str(result).split(",")
            if len(parts) >= 4:
                return {
                    "cash": float(parts[0]),
                    "total_assets": float(parts[1]),
                    "positions_value": float(parts[2]),
                    "available_cash": float(parts[3]),
                }

            return {}

        except Exception:
            return {}
