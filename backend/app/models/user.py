from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    """User model for authentication and QMT account linkage."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    qmt_user: Mapped[str | None] = mapped_column(String(64), nullable=True)
    qmt_password: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Relationships
    strategies: Mapped[list["Strategy"]] = relationship("Strategy", back_populates="user")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    positions: Mapped[list["Position"]] = relationship("Position", back_populates="user")
