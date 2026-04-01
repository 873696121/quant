"""Backtest engine core implementation."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategy import Strategy, StrategyMode
from app.models.order import Order, OrderDirection, OrderType, OrderStatus, OrderMode
from app.models.position import Position, PositionMode


class BacktestEngine:
    """回测引擎"""

    def __init__(
        self,
        strategy_id: int,
        db: AsyncSession,
        initial_cash: float = 1000000.0,
    ):
        self.strategy_id = strategy_id
        self.db = db
        self.initial_cash = Decimal(str(initial_cash))
        self.cash = self.initial_cash
        self.orders: list[Order] = []
        self.positions: dict[str, Position] = {}
        self.strategy: Optional[Strategy] = None
        self._running = False

        # 回测参数
        self.commission_rate = Decimal("0.0003")  # 万3佣金
        self.stamp_tax_rate = Decimal("0.001")    # 千1印花税(卖出)
        self.market_data = None

    async def initialize(self):
        """初始化回测引擎，加载策略配置"""
        from app.services.strategy_service import StrategyService

        service = StrategyService(self.db)
        self.strategy = await service.get_by_id(self.strategy_id, user_id=None)
        if not self.strategy:
            raise ValueError(f"Strategy {self.strategy_id} not found")

        # 重置持仓和资金
        self.cash = self.initial_cash
        self.positions.clear()
        self.orders.clear()

    async def run(self, start_date: str, end_date: str) -> dict:
        """运行回测

        Args:
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD

        Returns:
            回测结果字典
        """
        self._running = True

        try:
            from .market_data import MarketDataProvider
            from .strategies import MeanReversionStrategy

            # 获取市场数据
            self.market_data = MarketDataProvider()

            # 解析日期
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()

            # 获取策略信号
            strategy_impl = MeanReversionStrategy(self.strategy.config or {})

            current_date = start
            while current_date <= end and self._running:
                # 获取当日市场数据
                market_data = await self.market_data.get_historical_data(
                    "000001", start_date, end_date, "daily"
                )

                if market_data is not None and not market_data.empty:
                    # 生成信号
                    signals = strategy_impl.generate_signals(market_data)

                    # 执行信号对应的订单
                    for signal in signals:
                        if signal["action"] == "buy":
                            await self._execute_buy(signal)
                        elif signal["action"] == "sell":
                            await self._execute_sell(signal)

                # 更新持仓
                await self._update_positions()

                # 下一个交易日
                current_date = self._next_trading_day(current_date)

            # 计算最终指标
            return await self.calculate_metrics()

        finally:
            self._running = False

    async def _execute_buy(self, signal: dict):
        """执行买入"""
        symbol = signal["symbol"]
        price = Decimal(str(signal.get("price", 0)))
        volume = signal.get("volume", 100)

        if price <= 0 or volume <= 0:
            return

        cost = price * volume
        commission = cost * self.commission_rate

        if cost + commission > self.cash:
            volume = int(self.cash / (price * (1 + self.commission_rate)))
            if volume <= 0:
                return

        order = Order(
            user_id=self.strategy.user_id,
            strategy_id=self.strategy_id,
            symbol=symbol,
            direction=OrderDirection.BUY,
            order_type=OrderType.MARKET,
            price=price,
            volume=volume,
            filled_volume=volume,
            status=OrderStatus.FILLED,
            mode=OrderMode.BACKTEST,
        )
        self.db.add(order)

        self.cash -= price * volume + price * volume * self.commission_rate

        if symbol in self.positions:
            pos = self.positions[symbol]
            total_vol = pos.volume + volume
            pos.avg_cost = (pos.avg_cost * pos.volume + price * volume) / total_vol
            pos.volume = total_vol
        else:
            self.positions[symbol] = Position(
                user_id=self.strategy.user_id,
                strategy_id=self.strategy_id,
                symbol=symbol,
                volume=volume,
                avg_cost=price,
                frozen_volume=0,
                mode=PositionMode.BACKTEST,
            )

        self.orders.append(order)

    async def _execute_sell(self, signal: dict):
        """执行卖出"""
        symbol = signal["symbol"]
        price = Decimal(str(signal.get("price", 0)))
        volume = signal.get("volume", 100)

        if symbol not in self.positions:
            return

        pos = self.positions[symbol]
        volume = min(volume, pos.volume)

        if volume <= 0 or price <= 0:
            return

        order = Order(
            user_id=self.strategy.user_id,
            strategy_id=self.strategy_id,
            symbol=symbol,
            direction=OrderDirection.SELL,
            order_type=OrderType.MARKET,
            price=price,
            volume=volume,
            filled_volume=volume,
            status=OrderStatus.FILLED,
            mode=OrderMode.BACKTEST,
        )
        self.db.add(order)

        revenue = price * volume
        stamp_tax = revenue * self.stamp_tax_rate
        commission = revenue * self.commission_rate

        self.cash += revenue - stamp_tax - commission
        pos.volume -= volume

        if pos.volume <= 0:
            del self.positions[symbol]

        self.orders.append(order)

    async def _update_positions(self):
        """更新持仓成本和盈亏"""
        pass

    async def calculate_metrics(self) -> dict:
        """计算回测指标"""
        final_assets = self.cash
        for pos in self.positions.values():
            final_assets += pos.avg_cost * pos.volume

        total_return = (final_assets - self.initial_cash) / self.initial_cash * 100

        # 计算最大回撤
        max_drawdown = 0.0
        cumulative = self.initial_cash

        for order in self.orders:
            if order.direction == OrderDirection.BUY:
                cumulative -= order.price * order.filled_volume
            else:
                cumulative += order.price * order.filled_volume

            if cumulative < self.initial_cash:
                drawdown = (self.initial_cash - cumulative) / self.initial_cash * 100
                max_drawdown = max(max_drawdown, drawdown)

        return {
            "initial_cash": float(self.initial_cash),
            "final_assets": float(final_assets),
            "total_return": round(total_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "total_orders": len(self.orders),
            "positions": {
                symbol: {
                    "volume": pos.volume,
                    "avg_cost": float(pos.avg_cost),
                }
                for symbol, pos in self.positions.items()
            },
        }

    def _next_trading_day(self, current: date) -> date:
        """获取下一个交易日（简单实现：工作日+1）"""
        from datetime import timedelta
        return current + timedelta(days=1)

    def stop(self):
        """停止回测"""
        self._running = False
