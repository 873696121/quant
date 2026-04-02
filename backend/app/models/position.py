from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, Enum as SQLEnum, Numeric, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PositionMode(str):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


position_mode_enum = SQLEnum(
    PositionMode.BACKTEST,
    PositionMode.PAPER,
    PositionMode.LIVE,
    name="position_mode",
)


class Position(Base):
    """Position model for tracking user positions across different modes."""

    __tablename__ = "positions"
    __table_args__ = (
        UniqueConstraint("user_id", "symbol", "mode", name="uq_user_symbol_mode"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(16), nullable=False)
    volume: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"), nullable=False)
    current_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    frozen_volume: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mode: Mapped[PositionMode] = mapped_column(position_mode_enum, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="positions")

    def to_domain(self) -> 'Position':
        """转换为领域对象"""
        from domain.trading.aggregates.position import Position
        from domain.trading.value_objects.position_mode import PositionModeEnum
        return Position(
            id=self.id,
            user_id=self.user_id,
            symbol=self.symbol,
            volume=self.volume,
            frozen_volume=self.frozen_volume,
            avg_cost=float(self.avg_cost) if self.avg_cost else 0.0,
            current_price=float(self.current_price) if self.current_price else 0.0,
            mode=PositionModeEnum(self.mode.value),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
