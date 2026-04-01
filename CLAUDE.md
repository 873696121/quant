# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quant 量化交易系统 - A quantitative trading research and execution platform for A-shares, supporting backtesting, paper trading, and live trading via QMT (MiniQMT).

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + Element Plus + ECharts + Pinia |
| Backend | Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) |
| Database | MySQL 8.0 |
| Cache | Redis 7 |
| Market Data | akshare, tushare |
| Live Trading | QMT (MiniQMT) Python API |
| Deployment | Docker + Docker Compose |

## Common Commands

### Setup & Startup
```bash
./setup.sh          # Initialize: check Docker, create .env, start MySQL/Redis
./start.sh          # Start all services via docker compose
docker compose up -d          # Start all services
docker compose logs -f        # View logs
docker compose down           # Stop services
docker compose restart        # Restart services
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt          # Install dependencies
uvicorn app.main:app --reload           # Run with hot reload (port 8000)
alembic upgrade head                     # Run migrations
```

### Frontend Development
```bash
cd frontend
npm install                             # Install dependencies
npm run dev                              # Dev server (port 3000)
npm run build                            # Production build
```

### Testing
```bash
# Backend - run pytest or unittest
cd backend && python -m pytest

# Frontend - run tests
cd frontend && npm run test
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Vue 3)                  │
│   Dashboard │ Market │ Strategy │ Order Pages       │
├─────────────────────────────────────────────────────┤
│               API Service Layer (FastAPI)            │
│   Auth │ Strategies │ Orders │ Market │ Dashboard  │
├─────────────────────────────────────────────────────┤
│                    Engine Layer                      │
│      Backtest Engine │ Simulated Execution           │
├─────────────────────────────────────────────────────┤
│                    Data Layer                        │
│   akshare/tushare → MySQL │ Redis Cache │ QMT API   │
└─────────────────────────────────────────────────────┘
```

## Backend Structure (`backend/app/`)

- `api/routes.py` - All API endpoints (auth, strategies, orders, market, dashboard)
- `core/` - Core modules: `config.py` (settings), `database.py` (async SQLAlchemy), `security.py` (JWT/bcrypt)
- `models/` - SQLAlchemy models: `user.py`, `strategy.py`, `order.py`, `position.py`, `backtest.py`, `market.py`
- `schemas/` - Pydantic request/response schemas
- `services/` - Business logic: `auth_service.py`, `strategy_service.py`, `order_service.py`, `market_service.py`, `dashboard_service.py`
- `engine/` - Backtest engine (placeholder)
- `executors/` - Execution engines (simulated, QMT)

## Frontend Structure (`frontend/src/`)

- `views/` - Pages: `Dashboard.vue`, `Market.vue`, `Strategy.vue`, `Order.vue`, `Login.vue`
- `api/` - Axios request modules
- `stores/` - Pinia stores for auth state
- `router/` - Vue Router with auth guards

## Execution Modes

Strategies support three modes configured per strategy:
- `backtest` - Historical data, simulated fill, mock fees
- `paper` - Real-time quotes, simulated fill, real fees
- `live` - Real-time quotes, QMT real orders

## Key Configuration

Environment variables (`.env`):
- `DB_*` - MySQL connection settings
- `REDIS_*` - Redis connection settings
- `DEBUG=true` - Enable debug mode
- `SECRET_KEY` - JWT signing key

## API Endpoints

All endpoints under `/api` require JWT Bearer token except:
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /health` - Health check

## Database

- MySQL 8.0 with async SQLAlchemy 2.0
- Models use `async_sessionmaker` for async operations
- Alembic for migrations

## Data Sources

- **akshare** - Primary for A-share historical and real-time data
- **tushare** - Alternative data source (requires token)
- **QMT** - Live trading execution (runs on user's local machine)