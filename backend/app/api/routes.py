"""API routes aggregation module.

Implements all API endpoints for the quant trading system.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.market import QuoteResponse, KlineResponse, SearchResult, DashboardSummary, PositionResponse
from app.services.auth_service import AuthService
from app.services.strategy_service import StrategyService
from app.services.order_service import OrderService
from app.services.market_service import MarketService
from app.services.dashboard_service import DashboardService

# Main API router
api_router = APIRouter(prefix="/api")

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get current authenticated user."""
    token_data = decode_access_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = await db.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ============== Auth Endpoints ==============

@api_router.post("/auth/register", response_model=TokenResponse, tags=["auth"])
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    service = AuthService(db)
    try:
        user = await service.register(user_data)
        return service.create_token(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login and get access token."""
    service = AuthService(db)
    try:
        user = await service.authenticate(user_data.username, user_data.password)
        return service.create_token(user)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@api_router.get("/auth/me", response_model=UserResponse, tags=["auth"])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user info."""
    return UserResponse.model_validate(current_user)


# ============== Strategy Endpoints ==============

@api_router.get("/strategies", response_model=list[StrategyResponse], tags=["strategies"])
async def list_strategies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all strategies for current user."""
    service = StrategyService(db)
    strategies = await service.list_by_user(current_user.id)
    return [StrategyResponse.model_validate(s) for s in strategies]


@api_router.post("/strategies", response_model=StrategyResponse, tags=["strategies"])
async def create_strategy(
    data: StrategyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new strategy."""
    service = StrategyService(db)
    strategy = await service.create(current_user.id, data)
    return StrategyResponse.model_validate(strategy)


@api_router.get("/strategies/{strategy_id}", response_model=StrategyResponse, tags=["strategies"])
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a strategy by ID."""
    service = StrategyService(db)
    strategy = await service.get_by_id(strategy_id, current_user.id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return StrategyResponse.model_validate(strategy)


@api_router.put("/strategies/{strategy_id}", response_model=StrategyResponse, tags=["strategies"])
async def update_strategy(
    strategy_id: int,
    data: StrategyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a strategy."""
    service = StrategyService(db)
    strategy = await service.update(strategy_id, current_user.id, data)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return StrategyResponse.model_validate(strategy)


@api_router.delete("/strategies/{strategy_id}", tags=["strategies"])
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a strategy."""
    service = StrategyService(db)
    success = await service.delete(strategy_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "Strategy deleted"}


# ============== Order Endpoints ==============

@api_router.get("/orders", response_model=list[OrderResponse], tags=["orders"])
async def list_orders(
    mode: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List orders for current user."""
    service = OrderService(db)
    orders = await service.list_orders(current_user.id, mode, status)
    return [OrderResponse.model_validate(o) for o in orders]


@api_router.post("/orders", response_model=OrderResponse, tags=["orders"])
async def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new order (simulated fill)."""
    service = OrderService(db)
    order = await service.create_order(current_user.id, data)
    return OrderResponse.model_validate(order)


@api_router.delete("/orders/{order_id}", tags=["orders"])
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an order."""
    service = OrderService(db)
    success = await service.cancel_order(order_id, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel order")
    return {"message": "Order cancelled"}


# ============== Market Endpoints ==============

@api_router.get("/market/quote/{symbol}", response_model=QuoteResponse, tags=["market"])
async def get_quote(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """Get real-time quote for a symbol."""
    service = MarketService()
    try:
        quote = await service.get_quote(symbol)
        return quote
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/market/quotes", response_model=list[QuoteResponse], tags=["market"])
async def get_quotes(
    codes: list[str],
    current_user: User = Depends(get_current_user),
):
    """Get quotes for multiple symbols."""
    service = MarketService()
    quotes = await service.get_quotes(codes)
    return quotes


@api_router.get("/market/kline/{symbol}", response_model=KlineResponse, tags=["market"])
async def get_kline(
    symbol: str,
    period: str = Query("daily"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get kline data for a symbol."""
    service = MarketService()
    try:
        kline = await service.get_kline(symbol, period, start_date, end_date)
        return kline
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/market/search", response_model=list[SearchResult], tags=["market"])
async def search_stock(
    keyword: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    """Search stocks by keyword."""
    service = MarketService()
    try:
        results = await service.search(keyword)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============== Dashboard Endpoints ==============

@api_router.get("/dashboard/summary", response_model=DashboardSummary, tags=["dashboard"])
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard summary."""
    service = DashboardService(db)
    summary = await service.get_summary(current_user.id)
    return summary


@api_router.get("/dashboard/positions", response_model=list[PositionResponse], tags=["dashboard"])
async def get_dashboard_positions(
    mode: str = Query("paper"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get positions for dashboard."""
    service = DashboardService(db)
    positions = await service.get_positions(current_user.id, mode)
    return positions
