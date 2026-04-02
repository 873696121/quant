from typing import Optional, List
from app.domain.strategy.aggregates.strategy import Strategy, Backtest


class StrategyRepository:
    """策略仓储接口"""

    async def find_by_id(self, strategy_id: int) -> Optional[Strategy]:
        raise NotImplementedError

    async def find_by_user_id(self, user_id: int) -> List[Strategy]:
        raise NotImplementedError

    async def save(self, strategy: Strategy) -> Strategy:
        raise NotImplementedError

    async def delete(self, strategy_id: int) -> None:
        raise NotImplementedError


class BacktestRepository:
    """回测仓储接口"""

    async def find_by_id(self, backtest_id: int) -> Optional[Backtest]:
        raise NotImplementedError

    async def find_by_strategy_id(self, strategy_id: int) -> List[Backtest]:
        raise NotImplementedError

    async def save(self, backtest: Backtest) -> Backtest:
        raise NotImplementedError
