from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class OrderDirection(str):
    BUY = "buy"
    SELL = "sell"


class OrderType(str):
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(str):
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderMode(str):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


order_direction_enum = SQLEnum(OrderDirection.BUY, OrderDirection.SELL, name="order_direction")
order_type_enum = SQLEnum(OrderType.MARKET, OrderType.LIMIT, name="order_type")
order_status_enum = SQLEnum(
    OrderStatus.PENDING,
    OrderStatus.SUBMITTED,
    OrderStatus.FILLED,
    OrderStatus.CANCELLED,
    OrderStatus.REJECTED,
    name="order_status",
)
order_mode_enum = SQLEnum(
    OrderMode.BACKTEST,
    OrderMode.PAPER,
    OrderMode.LIVE,
    name="order_mode",
)


class Order(Base):
    """Order model for storing trading orders."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    backtest_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("backtests.id"), nullable=True)
    symbol: Mapped[str] = mapped_column(String(16), nullable=False)
    direction: Mapped[OrderDirection] = mapped_column(order_direction_enum, nullable=False)
    order_type: Mapped[OrderType] = mapped_column(
        order_type_enum,
        default=OrderType.LIMIT,
        nullable=False,
    )
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)
    filled_volume: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        order_status_enum,
        default=OrderStatus.PENDING,
        nullable=False,
    )
    mode: Mapped[OrderMode] = mapped_column(order_mode_enum, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    backtest: Mapped[Optional["Backtest"]] = relationship("Backtest", back_populates="orders")
