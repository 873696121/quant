from typing import Optional, List

from sqlalchemy import Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class StrategyMode(str):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


strategy_mode_enum = SQLEnum(
    StrategyMode.BACKTEST,
    StrategyMode.PAPER,
    StrategyMode.LIVE,
    name="strategy_mode",
)


class Strategy(Base):
    """Strategy model for storing trading strategies."""

    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[StrategyMode] = mapped_column(
        strategy_mode_enum,
        default=StrategyMode.BACKTEST,
        nullable=False,
    )
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="strategies")
    backtests: Mapped[List["Backtest"]] = relationship("Backtest", back_populates="strategy")
