from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import Integer, String, ForeignKey, Enum as SQLEnum, Date, Numeric
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class BacktestStatus(str):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


backtest_status_enum = SQLEnum(
    BacktestStatus.PENDING,
    BacktestStatus.RUNNING,
    BacktestStatus.COMPLETED,
    BacktestStatus.FAILED,
    name="backtest_status",
)


class Backtest(Base):
    """Backtest model for storing backtest configurations and results."""

    __tablename__ = "backtests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    strategy_id: Mapped[int] = mapped_column(Integer, ForeignKey("strategies.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    initial_cash: Mapped[Decimal] = mapped_column(
        Numeric(16, 2),
        default=Decimal("1000000"),
        nullable=False,
    )
    result_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[BacktestStatus] = mapped_column(
        backtest_status_enum,
        default=BacktestStatus.PENDING,
        nullable=False,
    )

    # Relationships
    strategy: Mapped["Strategy"] = relationship("Strategy", back_populates="backtests")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="backtest")
