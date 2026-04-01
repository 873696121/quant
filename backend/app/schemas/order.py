"""Order schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """Schema for creating an order."""
    symbol: str = Field(..., pattern=r"^\d{6}\.(SH|SZ)$")
    direction: str = Field(..., pattern="^(buy|sell)$")
    order_type: str = Field(default="limit")
    price: Optional[Decimal] = Field(None, ge=0)
    volume: int = Field(..., gt=0)
    mode: str = Field(default="paper")


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: int
    user_id: int
    symbol: str
    direction: str
    order_type: str
    price: Optional[Decimal]
    volume: int
    filled_volume: int
    status: str
    mode: str
    created_at: datetime

    model_config = {"from_attributes": True}
