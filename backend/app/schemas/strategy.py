"""Strategy schemas."""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class StrategyCreate(BaseModel):
    """Schema for creating a strategy."""
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None
    code: str = Field(..., min_length=1)
    mode: Literal["backtest", "paper", "live"] = Field(default="backtest")
    config: Optional[dict] = None


class StrategyUpdate(BaseModel):
    """Schema for updating a strategy."""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = None
    code: Optional[str] = None
    mode: Optional[Literal["backtest", "paper", "live"]] = None
    config: Optional[dict] = None


class StrategyResponse(BaseModel):
    """Schema for strategy response."""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    code: str
    mode: str
    config: Optional[dict]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
