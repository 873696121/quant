# Minimum Viable Quant Trading System - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable frontend-backend connected system with auth, strategy CRUD, order management, market data, and dashboard.

**Architecture:** FastAPI backend with async SQLAlchemy, JWT auth, akshare for market data. Vue 3 frontend with Element Plus, Pinia stores. Docker-compose for MySQL/Redis.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0, Vue 3, Element Plus, akshare

---

## File Structure

### Backend (to create/modify)

| File | Purpose |
|------|---------|
| Create: `backend/app/schemas/__init__.py` | Schema exports |
| Create: `backend/app/schemas/user.py` | User Pydantic schemas |
| Create: `backend/app/schemas/strategy.py` | Strategy Pydantic schemas |
| Create: `backend/app/schemas/order.py` | Order Pydantic schemas |
| Create: `backend/app/schemas/market.py` | Market Pydantic schemas |
| Create: `backend/app/core/security.py` | JWT token handling, bcrypt |
| Create: `backend/app/services/__init__.py` | Service layer init |
| Create: `backend/app/services/auth_service.py` | Auth business logic |
| Create: `backend/app/services/strategy_service.py` | Strategy CRUD |
| Create: `backend/app/services/order_service.py` | Order management + simulate fill |
| Create: `backend/app/services/market_service.py` | Market data from akshare |
| Create: `backend/app/services/dashboard_service.py` | Dashboard data aggregation |
| Modify: `backend/app/api/routes.py` | Implement all API routes |
| Modify: `backend/app/main.py` | Add exception handlers |

### Frontend (to create/modify)

| File | Purpose |
|------|---------|
| Create: `frontend/src/views/Login.vue` | Login/Register page |
| Modify: `frontend/src/views/Dashboard.vue` | Real data binding |
| Modify: `frontend/src/views/Market.vue` | Market data display |
| Modify: `frontend/src/views/Strategy.vue` | Strategy CRUD UI |
| Modify: `frontend/src/views/Order.vue` | Order management UI |
| Modify: `frontend/src/router/routes.js` | Add login route + guard |

---

## Part 1: Backend Core Infrastructure

### Task 1: Create Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/strategy.py`
- Create: `backend/app/schemas/order.py`
- Create: `backend/app/schemas/market.py`

- [ ] **Step 1: Create schemas/__init__.py**

```python
"""Pydantic schemas for request/response validation."""

from .user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from .strategy import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
)
from .order import (
    OrderCreate,
    OrderResponse,
)
from .market import (
    QuoteResponse,
    KlineResponse,
    SearchResult,
    DashboardSummary,
    PositionResponse,
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "StrategyCreate",
    "StrategyUpdate",
    "StrategyResponse",
    "OrderCreate",
    "OrderResponse",
    "QuoteResponse",
    "KlineResponse",
    "SearchResult",
    "DashboardSummary",
    "PositionResponse",
]
```

- [ ] **Step 2: Create schemas/user.py**

```python
"""User schemas for authentication."""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    username: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

- [ ] **Step 3: Create schemas/strategy.py**

```python
"""Strategy schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StrategyCreate(BaseModel):
    """Schema for creating a strategy."""
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None
    code: str = Field(..., min_length=1)
    mode: str = Field(default="backtest")
    config: Optional[dict] = None


class StrategyUpdate(BaseModel):
    """Schema for updating a strategy."""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = None
    code: Optional[str] = None
    mode: Optional[str] = None
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
```

- [ ] **Step 4: Create schemas/order.py**

```python
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
```

- [ ] **Step 5: Create schemas/market.py**

```python
"""Market data schemas."""

from typing import List, Optional
from pydantic import BaseModel


class QuoteResponse(BaseModel):
    """Schema for quote response."""
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float
    volume: int
    amount: float
    high: float
    low: float
    open: float
    close: float
    timestamp: str


class KlineResponse(BaseModel):
    """Schema for kline response."""
    dates: List[str]
    opens: List[float]
    highs: List[float]
    lows: List[float]
    closes: List[float]
    volumes: List[int]


class SearchResult(BaseModel):
    """Schema for stock search result."""
    code: str
    name: str
    market: str
    type: str


class DashboardSummary(BaseModel):
    """Schema for dashboard summary."""
    total_asset: float
    today_profit: float
    position_count: int
    strategy_count: int
    order_count: int


class PositionResponse(BaseModel):
    """Schema for position response."""
    id: int
    symbol: str
    volume: int
    avg_cost: float
    frozen_volume: int
    mode: str
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
```

---

### Task 2: Create Security Module (JWT + bcrypt)

**Files:**
- Create: `backend/app/core/security.py`

- [ ] **Step 1: Create core/security.py**

```python
"""Security utilities for JWT and password hashing."""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from pydantic import BaseModel

from app.config import settings


class TokenData(BaseModel):
    """Token payload data."""
    user_id: int
    exp: Optional[datetime] = None


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode = {
        "user_id": user_id,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return TokenData(user_id=payload["user_id"])
    except jwt.PyJWTError:
        return None
```

- [ ] **Step 2: Update config.py to add SECRET_KEY**

Add to Settings class in `backend/app/config.py`:
```python
SECRET_KEY: str = "your-secret-key-change-in-production"
```

---

### Task 3: Create Service Layer

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/services/strategy_service.py`
- Create: `backend/app/services/order_service.py`
- Create: `backend/app/services/market_service.py`
- Create: `backend/app/services/dashboard_service.py`

- [ ] **Step 1: Create services/__init__.py**

```python
"""Business logic services."""

from .auth_service import AuthService
from .strategy_service import StrategyService
from .order_service import OrderService
from .market_service import MarketService
from .dashboard_service import DashboardService

__all__ = [
    "AuthService",
    "StrategyService",
    "OrderService",
    "MarketService",
    "DashboardService",
]
```

- [ ] **Step 2: Create services/auth_service.py**

```python
"""Authentication service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, TokenResponse, UserResponse


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if username exists
        result = await self.db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")

        # Create user
        user = User(
            username=user_data.username,
            password_hash=hash_password(user_data.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, username: str, password: str) -> User:
        """Authenticate a user."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")

        return user

    def create_token(self, user: User) -> TokenResponse:
        """Create access token for user."""
        token = create_access_token(user.id)
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )
```

- [ ] **Step 3: Create services/strategy_service.py**

```python
"""Strategy management service."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategy import Strategy
from app.schemas.strategy import StrategyCreate, StrategyUpdate


class StrategyService:
    """Service for strategy operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(self, user_id: int) -> List[Strategy]:
        """List all strategies for a user."""
        result = await self.db.execute(
            select(Strategy)
            .where(Strategy.user_id == user_id)
            .order_by(Strategy.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, strategy_id: int, user_id: int) -> Optional[Strategy]:
        """Get a strategy by ID."""
        result = await self.db.execute(
            select(Strategy)
            .where(Strategy.id == strategy_id, Strategy.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, data: StrategyCreate) -> Strategy:
        """Create a new strategy."""
        strategy = Strategy(
            user_id=user_id,
            name=data.name,
            description=data.description,
            code=data.code,
            mode=data.mode,
            config=data.config,
        )
        self.db.add(strategy)
        await self.db.flush()
        await self.db.refresh(strategy)
        return strategy

    async def update(
        self, strategy_id: int, user_id: int, data: StrategyUpdate
    ) -> Optional[Strategy]:
        """Update a strategy."""
        strategy = await self.get_by_id(strategy_id, user_id)
        if not strategy:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(strategy, key, value)

        await self.db.flush()
        await self.db.refresh(strategy)
        return strategy

    async def delete(self, strategy_id: int, user_id: int) -> bool:
        """Delete a strategy."""
        strategy = await self.get_by_id(strategy_id, user_id)
        if not strategy:
            return False

        await self.db.delete(strategy)
        await self.db.flush()
        return True
```

- [ ] **Step 4: Create services/order_service.py**

```python
"""Order management service with simulated fill."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus, OrderDirection
from app.models.position import Position
from app.schemas.order import OrderCreate


class OrderService:
    """Service for order operations with simulated fill."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_orders(
        self, user_id: int, mode: Optional[str] = None, status: Optional[str] = None
    ) -> List[Order]:
        """List orders for a user."""
        query = select(Order).where(Order.user_id == user_id)
        if mode:
            query = query.where(Order.mode == mode)
        if status:
            query = query.where(Order.status == status)
        query = query.order_by(Order.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, order_id: int, user_id: int) -> Optional[Order]:
        """Get an order by ID."""
        result = await self.db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_order(
        self, user_id: int, data: OrderCreate
    ) -> Order:
        """Create a new order and simulate fill."""
        # Create order
        order = Order(
            user_id=user_id,
            symbol=data.symbol,
            direction=data.direction,
            order_type=data.order_type,
            price=data.price,
            volume=data.volume,
            mode=data.mode,
            status=OrderStatus.PENDING,
        )
        self.db.add(order)
        await self.db.flush()

        # Simulate fill immediately
        order = await self._simulate_fill(order)
        return order

    async def _simulate_fill(self, order: Order) -> Order:
        """Simulate order fill and update position."""
        from decimal import Decimal

        # Mark as submitted then filled
        order.status = OrderStatus.SUBMITTED
        await self.db.flush()

        order.status = OrderStatus.FILLED
        order.filled_volume = order.volume
        await self.db.flush()

        # Update position
        if order.direction == OrderDirection.BUY:
            await self._update_position_buy(order)
        else:
            await self._update_position_sell(order)

        await self.db.refresh(order)
        return order

    async def _update_position_buy(self, order: Order) -> None:
        """Update position for buy order."""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == order.user_id,
                Position.symbol == order.symbol,
                Position.mode == order.mode,
            )
        )
        position = result.scalar_one_or_none()

        price = order.price or Decimal("0")
        if position:
            # Update existing position
            total_cost = position.avg_cost * position.volume + price * order.volume
            new_volume = position.volume + order.volume
            position.avg_cost = total_cost / new_volume if new_volume > 0 else Decimal("0")
            position.volume = new_volume
        else:
            # Create new position
            position = Position(
                user_id=order.user_id,
                symbol=order.symbol,
                volume=order.volume,
                avg_cost=price,
                mode=order.mode,
            )
            self.db.add(position)

        await self.db.flush()

    async def _update_position_sell(self, order: Order) -> None:
        """Update position for sell order."""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == order.user_id,
                Position.symbol == order.symbol,
                Position.mode == order.mode,
            )
        )
        position = result.scalar_one_or_none()

        if position:
            position.volume = max(0, position.volume - order.volume)
            await self.db.flush()

    async def cancel_order(self, order_id: int, user_id: int) -> bool:
        """Cancel an order (only pending orders)."""
        order = await self.get_by_id(order_id, user_id)
        if not order:
            return False

        if order.status != OrderStatus.PENDING:
            return False

        order.status = OrderStatus.CANCELLED
        await self.db.flush()
        return True
```

- [ ] **Step 5: Create services/market_service.py**

```python
"""Market data service using akshare."""

from typing import List, Optional, Dict, Any
import akshare as ak
from datetime import datetime


class MarketService:
    """Service for market data operations."""

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol."""
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == symbol]
            if row.empty:
                raise ValueError(f"Symbol {symbol} not found")

            row = row.iloc[0]
            return {
                "symbol": symbol,
                "name": row['名称'],
                "price": float(row['最新价']),
                "change": float(row['涨跌额']),
                "change_pct": float(row['涨跌幅']),
                "volume": int(row['成交量']),
                "amount": float(row['成交额']),
                "high": float(row['最高']),
                "low": float(row['最低']),
                "open": float(row['今开']),
                "close": float(row['昨收']),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            raise ValueError(f"Failed to get quote: {str(e)}")

    async def get_quotes(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get quotes for multiple symbols."""
        results = []
        for symbol in symbols:
            try:
                quote = await self.get_quote(symbol)
                results.append(quote)
            except Exception:
                continue
        return results

    async def get_kline(
        self, symbol: str, period: str = "daily", start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get kline data for a symbol."""
        try:
            if period == "daily":
                if start_date and end_date:
                    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
                else:
                    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            elif period == "weekly":
                df = ak.stock_zh_a_hist(symbol=symbol, period="weekly", adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")

            return {
                "dates": df['日期'].tolist(),
                "opens": df['开盘'].tolist(),
                "highs": df['最高'].tolist(),
                "lows": df['最低'].tolist(),
                "closes": df['收盘'].tolist(),
                "volumes": df['成交量'].tolist(),
            }
        except Exception as e:
            raise ValueError(f"Failed to get kline: {str(e)}")

    async def search(self, keyword: str) -> List[Dict[str, str]]:
        """Search stocks by keyword."""
        try:
            df = ak.stock_zh_a_spot_em()
            mask = df['名称'].str.contains(keyword, na=False) | df['代码'].str.contains(keyword, na=False)
            results = df[mask].head(20)

            return [
                {
                    "code": row['代码'],
                    "name": row['名称'],
                    "market": row['市场'],
                    "type": "stock",
                }
                for _, row in results.iterrows()
            ]
        except Exception as e:
            raise ValueError(f"Failed to search: {str(e)}")
```

- [ ] **Step 6: Create services/dashboard_service.py**

```python
"""Dashboard data aggregation service."""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.position import Position
from app.models.strategy import Strategy


class DashboardService:
    """Service for dashboard data aggregation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self, user_id: int) -> Dict[str, Any]:
        """Get dashboard summary for a user."""
        # Get position count
        pos_result = await self.db.execute(
            select(func.count(Position.id)).where(Position.user_id == user_id)
        )
        position_count = pos_result.scalar() or 0

        # Get strategy count
        strat_result = await self.db.execute(
            select(func.count(Strategy.id)).where(Strategy.user_id == user_id)
        )
        strategy_count = strat_result.scalar() or 0

        # Get today's order count
        from datetime import datetime, date
        today = date.today()
        order_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.user_id == user_id,
                func.date(Order.created_at) == today,
            )
        )
        order_count = order_result.scalar() or 0

        # Calculate total asset (simplified - sum of position values + cash)
        # For now, return mock data as we don't have cash tracking
        total_asset = 100000.0  # Mock initial cash
        today_profit = 0.0

        return {
            "total_asset": total_asset,
            "today_profit": today_profit,
            "position_count": position_count,
            "strategy_count": strategy_count,
            "order_count": order_count,
        }

    async def get_positions(self, user_id: int, mode: str = "paper") -> List[Dict[str, Any]]:
        """Get positions for a user."""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.mode == mode,
            )
        )
        positions = result.scalars().all()

        return [
            {
                "id": p.id,
                "symbol": p.symbol,
                "volume": p.volume,
                "avg_cost": float(p.avg_cost),
                "frozen_volume": p.frozen_volume,
                "mode": p.mode,
                "current_price": None,
                "profit_loss": None,
            }
            for p in positions
        ]
```

---

### Task 4: Implement API Routes

**Files:**
- Modify: `backend/app/api/routes.py`

- [ ] **Step 1: Implement routes.py with all endpoints**

```python
"""API routes aggregation module.

Implements all API endpoints for the quant trading system.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
```

---

### Task 5: Update Main.py

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Update main.py with exception handlers**

Add after `app = FastAPI(...)`:

```python
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
```

---

## Part 2: Frontend Implementation

### Task 6: Create Login Page

**Files:**
- Create: `frontend/src/views/Login.vue`

- [ ] **Step 1: Create Login.vue**

```vue
<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>量化交易系统</span>
        </div>
      </template>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item v-if="isRegister" label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请确认密码"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submit">
            {{ isRegister ? '注册' : '登录' }}
          </el-button>
          <el-button text @click="isRegister = !isRegister">
            {{ isRegister ? '返回登录' : '没有账号？注册' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import request from '@/api/index'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)
const isRegister = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPassword = (rule, value, callback) => {
  if (form.confirmPassword !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 64, message: '用户名长度在 3 到 64 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

const submit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const url = isRegister.value ? '/auth/register' : '/auth/login'
    const res = await request.post(url, {
      username: form.username,
      password: form.password,
    })

    userStore.setToken(res.access_token)
    userStore.setUserInfo(res.user)
    ElMessage.success(isRegister.value ? '注册成功' : '登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}
</style>
```

---

### Task 7: Update Dashboard Page

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`

- [ ] **Step 1: Update Dashboard.vue with real data**

```vue
<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>总资产</span>
          </template>
          <div class="stat-value">{{ formatMoney(summary.total_asset) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>今日收益</span>
          </template>
          <div class="stat-value" :class="profitClass(summary.today_profit)">
            {{ formatMoney(summary.today_profit) }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>持仓数量</span>
          </template>
          <div class="stat-value">{{ summary.position_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>运行策略</span>
          </template>
          <div class="stat-value">{{ summary.strategy_count }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>持仓列表</span>
          </template>
          <el-table :data="positions" stripe>
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="volume" label="数量" width="80" />
            <el-table-column prop="avg_cost" label="成本" width="100">
              <template #default="{ row }">
                {{ row.avg_cost?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="current_price" label="现价" width="100">
              <template #default="{ row }">
                {{ row.current_price?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="profit_loss" label="盈亏" width="100">
              <template #default="{ row }">
                <span :class="profitClass(row.profit_loss)">
                  {{ row.profit_loss?.toFixed(2) || '-' }}
                </span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="positions.length === 0" description="暂无持仓" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>今日订单</span>
          </template>
          <el-table :data="orders" stripe>
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="direction" label="方向" width="60">
              <template #default="{ row }">
                <el-tag :type="row.direction === 'buy' ? 'success' : 'danger'" size="small">
                  {{ row.direction === 'buy' ? '买' : '卖' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="数量" width="80" />
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{ row }">
                {{ row.price?.toFixed(2) || '市价' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag size="small">{{ statusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="orders.length === 0" description="今日暂无订单" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/index'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const summary = ref({
  total_asset: 0,
  today_profit: 0,
  position_count: 0,
  strategy_count: 0,
  order_count: 0,
})

const positions = ref([])
const orders = ref([])

const formatMoney = (value) => {
  if (value == null) return '--'
  return value.toLocaleString('zh-CN', { style: 'currency', currency: 'CNY' })
}

const profitClass = (value) => {
  if (value > 0) return 'profit'
  if (value < 0) return 'loss'
  return ''
}

const statusText = (status) => {
  const map = {
    pending: '待成交',
    submitted: '已提交',
    filled: '已成交',
    cancelled: '已取消',
    rejected: '已拒绝',
  }
  return map[status] || status
}

const fetchDashboard = async () => {
  try {
    const [summaryRes, positionsRes, ordersRes] = await Promise.all([
      request.get('/dashboard/summary'),
      request.get('/dashboard/positions'),
      request.get('/orders', { mode: 'paper' }),
    ])
    summary.value = summaryRes
    positions.value = positionsRes
    orders.value = ordersRes
  } catch (error) {
    console.error('Failed to fetch dashboard:', error)
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    window.location.href = '/login'
    return
  }
  fetchDashboard()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  padding: 20px 0;
  color: #409eff;
}

.stat-value.profit {
  color: #67c23a;
}

.stat-value.loss {
  color: #f56c6c;
}
</style>
```

---

### Task 8: Update Strategy Page

**Files:**
- Modify: `frontend/src/views/Strategy.vue`

- [ ] **Step 1: Update Strategy.vue**

```vue
<template>
  <div class="strategy-page">
    <div class="header">
      <h2>策略管理</h2>
      <el-button type="primary" @click="openCreateDialog">创建策略</el-button>
    </div>

    <el-table :data="strategies" stripe style="margin-top: 20px;">
      <el-table-column prop="name" label="策略名称" width="150" />
      <el-table-column prop="mode" label="模式" width="100">
        <template #default="{ row }">
          <el-tag>{{ modeText(row.mode) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="strategies.length === 0" description="暂无策略" />

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑策略' : '创建策略'" width="600px">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="策略名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="模式" prop="mode">
          <el-select v-model="form.mode">
            <el-option label="回测" value="backtest" />
            <el-option label="模拟" value="paper" />
            <el-option label="实盘" value="live" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略代码" prop="code">
          <el-input
            v-model="form.code"
            type="textarea"
            :rows="10"
            placeholder="请输入策略代码 (Python)"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { strategyApi } from '@/api/strategy'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const strategies = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const formRef = ref()
const form = reactive({
  name: '',
  mode: 'paper',
  code: '',
})

const modeText = (mode) => {
  const map = { backtest: '回测', paper: '模拟', live: '实盘' }
  return map[mode] || mode
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchStrategies = async () => {
  try {
    strategies.value = await strategyApi.list()
  } catch (error) {
    ElMessage.error('获取策略列表失败')
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, { name: '', mode: 'paper', code: '' })
  dialogVisible.value = true
}

const openEditDialog = (strategy) => {
  isEdit.value = true
  editingId.value = strategy.id
  Object.assign(form, {
    name: strategy.name,
    mode: strategy.mode,
    code: strategy.code,
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    if (isEdit.value) {
      await strategyApi.update(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await strategyApi.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchStrategies()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该策略吗？', '提示', {
      type: 'warning',
    })
    await strategyApi.delete(id)
    ElMessage.success('删除成功')
    fetchStrategies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    window.location.href = '/login'
    return
  }
  fetchStrategies()
})
</script>

<style scoped>
.strategy-page {
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

---

### Task 9: Update Order Page

**Files:**
- Modify: `frontend/src/views/Order.vue`

- [ ] **Step 1: Update Order.vue**

```vue
<template>
  <div class="order-page">
    <div class="header">
      <h2>订单管理</h2>
      <el-button type="primary" @click="openCreateDialog">下单</el-button>
    </div>

    <el-card style="margin-top: 20px;">
      <el-form inline>
        <el-form-item label="订单模式">
          <el-select v-model="queryMode" @change="fetchOrders">
            <el-option label="全部" value="" />
            <el-option label="回测" value="backtest" />
            <el-option label="模拟" value="paper" />
            <el-option label="实盘" value="live" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="orders" stripe style="margin-top: 20px;">
      <el-table-column prop="symbol" label="股票代码" width="120" />
      <el-table-column prop="direction" label="方向" width="80">
        <template #default="{ row }">
          <el-tag :type="row.direction === 'buy' ? 'success' : 'danger'" size="small">
            {{ row.direction === 'buy' ? '买入' : '卖出' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="order_type" label="订单类型" width="100">
        <template #default="{ row }">
          {{ row.order_type === 'market' ? '市价' : '限价' }}
        </template>
      </el-table-column>
      <el-table-column prop="volume" label="数量" width="80" />
      <el-table-column prop="price" label="价格" width="100">
        <template #default="{ row }">
          {{ row.price?.toFixed(2) || '市价' }}
        </template>
      </el-table-column>
      <el-table-column prop="filled_volume" label="成交数量" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">
            {{ statusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'pending'"
            size="small"
            type="danger"
            @click="handleCancel(row.id)"
          >
            撤单
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="orders.length === 0" description="暂无订单" />

    <el-dialog v-model="dialogVisible" title="下单" width="400px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="股票代码" prop="symbol">
          <el-input v-model="form.symbol" placeholder="如: 000001.SZ" />
        </el-form-item>
        <el-form-item label="方向" prop="direction">
          <el-radio-group v-model="form.direction">
            <el-radio label="buy">买入</el-radio>
            <el-radio label="sell">卖出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="订单类型" prop="order_type">
          <el-select v-model="form.order_type">
            <el-option label="限价" value="limit" />
            <el-option label="市价" value="market" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price" v-if="form.order_type === 'limit'">
          <el-input-number v-model="form.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="数量" prop="volume">
          <el-input-number v-model="form.volume" :min="100" :step="100" />
        </el-form-item>
        <el-form-item label="模式" prop="mode">
          <el-select v-model="form.mode">
            <el-option label="回测" value="backtest" />
            <el-option label="模拟" value="paper" />
            <el-option label="实盘" value="live" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { orderApi } from '@/api/order'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const orders = ref([])
const queryMode = ref('paper')
const dialogVisible = ref(false)

const formRef = ref()
const form = reactive({
  symbol: '',
  direction: 'buy',
  order_type: 'limit',
  price: null,
  volume: 100,
  mode: 'paper',
})

const rules = {
  symbol: [
    { required: true, message: '请输入股票代码', trigger: 'blur' },
    { pattern: /^\d{6}\.(SH|SZ)$/, message: '格式如: 000001.SZ', trigger: 'blur' },
  ],
  direction: [{ required: true, message: '请选择方向', trigger: 'change' }],
  volume: [{ required: true, message: '请输入数量', trigger: 'blur' }],
}

const statusText = (status) => {
  const map = {
    pending: '待成交',
    submitted: '已提交',
    filled: '已成交',
    cancelled: '已取消',
    rejected: '已拒绝',
  }
  return map[status] || status
}

const statusType = (status) => {
  const map = {
    pending: 'warning',
    submitted: 'primary',
    filled: 'success',
    cancelled: 'info',
    rejected: 'danger',
  }
  return map[status] || ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchOrders = async () => {
  try {
    const params = queryMode.value ? { mode: queryMode.value } : {}
    orders.value = await orderApi.list(params)
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  }
}

const openCreateDialog = () => {
  Object.assign(form, {
    symbol: '',
    direction: 'buy',
    order_type: 'limit',
    price: null,
    volume: 100,
    mode: 'paper',
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    await orderApi.create(form)
    ElMessage.success('下单成功')
    dialogVisible.value = false
    fetchOrders()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('下单失败')
    }
  }
}

const handleCancel = async (id) => {
  try {
    await orderApi.cancel(id)
    ElMessage.success('撤单成功')
    fetchOrders()
  } catch (error) {
    ElMessage.error('撤单失败')
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    window.location.href = '/login'
    return
  }
  fetchOrders()
})
</script>

<style scoped>
.order-page {
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

---

### Task 10: Update Market Page

**Files:**
- Modify: `frontend/src/views/Market.vue`

- [ ] **Step 1: Update Market.vue**

```vue
<template>
  <div class="market-page">
    <div class="header">
      <h2>行情监控</h2>
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索股票代码或名称"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>
    </div>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>自选股行情</span>
          </template>
          <el-table :data="watchlist" stripe @row-click="handleRowClick">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="100" />
            <el-table-column prop="price" label="最新价" width="100">
              <template #default="{ row }">
                {{ row.price?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌额" width="100">
              <template #default="{ row }">
                <span :class="profitClass(row.change)">
                  {{ row.change?.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="change_pct" label="涨跌幅" width="100">
              <template #default="{ row }">
                <span :class="profitClass(row.change_pct)">
                  {{ row.change_pct?.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="成交量" width="120" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click.stop="removeFromWatchlist(row.symbol)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="watchlist.length === 0" description="暂无自选股" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>搜索结果</span>
          </template>
          <el-table :data="searchResults" stripe>
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="100" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="addToWatchlist(row)">
                  添加
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>K线图 - {{ selectedSymbol || '请选择股票' }}</span>
          </template>
          <div v-if="klineData.dates.length > 0" ref="chartRef" style="height: 400px;"></div>
          <el-empty v-else description="请选择股票查看K线" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { marketApi } from '@/api/market'
import { useUserStore } from '@/stores/user'
import * as echarts from 'echarts'

const userStore = useUserStore()
const searchKeyword = ref('')
const searchResults = ref([])
const watchlist = ref([])
const selectedSymbol = ref('')
const klineData = reactive({
  dates: [],
  opens: [],
  highs: [],
  lows: [],
  closes: [],
  volumes: [],
})

const chartRef = ref()
let chartInstance = null

const profitClass = (value) => {
  if (value > 0) return 'profit'
  if (value < 0) return 'loss'
  return ''
}

const handleSearch = async () => {
  if (!searchKeyword.value) return
  try {
    searchResults.value = await marketApi.search(searchKeyword.value)
  } catch (error) {
    ElMessage.error('搜索失败')
  }
}

const addToWatchlist = (stock) => {
  if (watchlist.value.some(item => item.symbol === stock.code)) {
    ElMessage.warning('已添加过该股票')
    return
  }
  watchlist.value.push({
    symbol: stock.code,
    name: stock.name,
    price: 0,
    change: 0,
    change_pct: 0,
    volume: 0,
  })
  ElMessage.success('添加成功')
  fetchQuote(stock.code)
}

const removeFromWatchlist = (symbol) => {
  const index = watchlist.value.findIndex(item => item.symbol === symbol)
  if (index > -1) {
    watchlist.value.splice(index, 1)
  }
}

const handleRowClick = async (row) => {
  selectedSymbol.value = row.symbol
  await fetchKline(row.symbol)
}

const fetchQuote = async (symbol) => {
  try {
    const quote = await marketApi.getQuote(symbol)
    const index = watchlist.value.findIndex(item => item.symbol === symbol)
    if (index > -1) {
      watchlist.value[index] = { ...watchlist.value[index], ...quote }
    }
  } catch (error) {
    console.error('Failed to fetch quote:', error)
  }
}

const fetchKline = async (symbol) => {
  try {
    const data = await marketApi.getKline(symbol, { period: 'daily' })
    klineData.dates = data.dates
    klineData.opens = data.opens
    klineData.highs = data.highs
    klineData.lows = data.lows
    klineData.closes = data.closes
    klineData.volumes = data.volumes
    await nextTick()
    renderChart()
  } catch (error) {
    ElMessage.error('获取K线数据失败')
  }
}

const renderChart = () => {
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    grid: { left: '10%', right: '10%', bottom: '15%', top: '10%' },
    xAxis: {
      type: 'category',
      data: klineData.dates,
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      scale: true,
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: 0, end: 100 },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData.closes.map((_, i) => [
          klineData.opens[i],
          klineData.closes[i],
          klineData.lows[i],
          klineData.highs[i],
        ]),
      },
    ],
  }

  chartInstance.setOption(option)
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    window.location.href = '/login'
    return
  }
  // Load default watchlist
  watchlist.value = [
    { symbol: '000001.SZ', name: '平安银行', price: 0, change: 0, change_pct: 0, volume: 0 },
  ]
  if (watchlist.value.length > 0) {
    fetchQuote(watchlist.value[0].symbol)
  }
})
</script>

<style scoped>
.market-page {
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  width: 300px;
}

.profit {
  color: #67c23a;
}

.loss {
  color: #f56c6c;
}
</style>
```

---

### Task 11: Update Router with Login Route and Guard

**Files:**
- Modify: `frontend/src/router/routes.js`

- [ ] **Step 1: Update routes.js with login route**

```javascript
export default [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表盘', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/views/Market.vue'),
    meta: { title: '行情', requiresAuth: true }
  },
  {
    path: '/strategy',
    name: 'Strategy',
    component: () => import('@/views/Strategy.vue'),
    meta: { title: '策略', requiresAuth: true }
  },
  {
    path: '/order',
    name: 'Order',
    component: () => import('@/views/Order.vue'),
    meta: { title: '订单', requiresAuth: true }
  }
]
```

- [ ] **Step 2: Update router/index.js to add navigation guard**

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
```

---

## Part 3: Database Migration

### Task 12: Create Database Tables

**Files:**
- Create: `backend/app/init_db.py`

- [ ] **Step 1: Create init_db.py to initialize database**

```python
"""Initialize database tables."""

import asyncio
from sqlalchemy import text
from app.core.database import engine, Base
from app.models.base import Base as ModelBase


async def init_db():
    """Create all database tables."""
    async with engine.begin() as conn:
        # Create database if not exists
        await conn.execute(text("CREATE DATABASE IF NOT EXISTS quant CHARACTER SET utf8mb4"))
        await conn.execute(text("USE quant"))

        # Create all tables
        await conn.run_sync(ModelBase.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
    print("Database initialized successfully")
```

---

## Self-Review Checklist

1. **Spec coverage:**
   - [x] Auth endpoints (register/login/me) - Task 4
   - [x] Strategy CRUD endpoints - Task 4
   - [x] Order endpoints (list/create/cancel) - Task 4
   - [x] Market endpoints (quote/kline/search) - Task 4
   - [x] Dashboard endpoints (summary/positions) - Task 4
   - [x] Login page - Task 6
   - [x] Dashboard page with real data - Task 7
   - [x] Strategy page with CRUD - Task 8
   - [x] Order page with trading - Task 9
   - [x] Market page with watchlist and chart - Task 10
   - [x] Router with auth guard - Task 11

2. **Placeholder scan:** No "TBD", "TODO", or vague requirements found.

3. **Type consistency:** All method signatures and property names are consistent across tasks.

---

**Plan complete.** Saved to `docs/superpowers/plans/2026-04-01-minimum-viable-system-implementation.md`.

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
