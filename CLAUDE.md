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
- `services/adapters/` - 数据源适配器: `base.py` (抽象接口), `akshare_adapter.py`, `tushare_adapter.py`
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

## Deployment Modes

系统支持两种部署模式，通过 `DEPLOYMENT` 环境变量控制：

```bash
DEPLOYMENT=local   # 本地开发/部署
DEPLOYMENT=cloud    # 云服务器部署
```

**本地部署配置示例 (`.env`)：**
```
DEPLOYMENT=local
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=3306
LOCAL_DB_USER=root
LOCAL_DB_PASSWORD=quant2026
LOCAL_DB_NAME=quant
LOCAL_REDIS_HOST=localhost
LOCAL_REDIS_PORT=6379
```

**云服务器部署配置示例 (`.env`)：**
```
DEPLOYMENT=cloud
CLOUD_HOST=115.190.198.148
CLOUD_DB_HOST=115.190.198.148
CLOUD_DB_PORT=3306
CLOUD_DB_USER=root
CLOUD_DB_PASSWORD=quant2026
CLOUD_DB_NAME=quant
CLOUD_REDIS_HOST=115.190.198.148
CLOUD_REDIS_PORT=6379
```

**启动服务：**
```bash
# 本地开发 - 直接启动
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker 部署
docker compose up -d

# 云服务器部署时，需要先运行数据库迁移
alembic upgrade head
```

## API Endpoints

All endpoints under `/api` require JWT Bearer token except:
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /health` - Health check

## Database

- MySQL 8.0 with async SQLAlchemy 2.0
- Models use `async_sessionmaker` for async operations
- Alembic for migrations

**重要：首次部署必须运行数据库迁移：**
```bash
cd backend
alembic upgrade head
```

如果遇到表结构问题，检查 `alembic/versions/` 下的迁移脚本是否与 `models/` 中的定义一致。

## Data Sources

### 配置方式
通过 `DATA_SOURCE` 环境变量配置数据源：
```
DATA_SOURCE=akshare   # 主要数据源（默认）
DATA_SOURCE=tushare   # 替代数据源（需要配置 TUSHARE_TOKEN）
```

### Market Service 架构
位于 `backend/app/services/market_service.py`，采用适配器模式：

```
数据源 API → Adapter (原始数据) → Formatter (系统格式) → API Response
```

**核心组件：**
- `DataSourceAdapter` - 抽象接口，定义 `get_quote`, `get_kline`, `search` 方法
- `AkshareAdapter` - akshare 实现（当前默认）
- `TushareAdapter` - tushare 实现（需配置 token）
- `MarketDataFormatter` - 将原始数据转换为系统统一格式
- `MarketService` - 主服务，根据配置调用对应 adapter

**切换数据源：**
```python
# 代码中指定
service = MarketService(data_source="tushare")

# 或通过环境变量（默认）
# DATA_SOURCE=akshare
service = MarketService()
```

### 重要原则
- **不使用 mock 数据** - 任何情况下都不允许降级到 mock 数据
- **统一数据格式** - 所有数据源获取的数据都通过 `MarketDataFormatter` 转换为系统格式
- **代理设置** - akshare 在某些网络环境下需要清除代理环境变量

### akshare 注意事项
- 部分接口（如 eastmoney）可能受代理影响
- 推荐使用 `stock_zh_a_hist_tx`（腾讯K线接口），该接口较稳定
- akshare 调用前会自动清除 `http_proxy`/`https_proxy` 环境变量

### tushare 配置
需要设置 token：
```
TUSHARE_TOKEN=your_token_here
```
访问 https://tushare.pro 注册申请

### 数据获取模式

MarketService 提供两种历史数据获取模式：

**1. 全量获取 (get_historical_full)**
- 用于首次加载或全量刷新
- 获取多年历史数据到当前日期
```python
# 获取10年历史数据
data = await service.get_historical_full("000001.SZ", period="daily", years=10)

# 批量获取
results = await service.batch_get_historical_full(
    ["000001.SZ", "600519.SH"],
    period="daily",
    years=5
)
```

**2. 增量获取 (get_historical_incremental)**
- 用于每日打开系统后查漏补缺
- 获取自 last_date 之后的新数据
```python
# 获取自上次更新以来的新数据
data = await service.get_historical_incremental(
    "000001.SZ",
    last_date="2026-03-25",  # YYYY-MM-DD 格式
    period="daily"
)

# 批量增量获取
results = await service.batch_get_historical_incremental(
    {"000001.SZ": "2026-03-25", "600519.SH": "2026-03-20"},
    period="daily"
)
```

### QMT
- Live trading execution (runs on user's local machine)
- 配置文件路径和连接参数

## Git Workflow

### 首次打开 Claude
如果项目不是 git 仓库（没有 `.git` 目录），自动初始化 git 仓库并创建初始提交：
```bash
git init
git add -A
git commit -m "init"
```

### 阶段性功能完成
当完成一个阶段性功能（feature、fix、refactor 等）时，自动创建 commit：
1. 使用 `git status` 查看变更
2. 使用 `git diff` 查看具体改动
3. 根据变更内容撰写 commit message（聚焦于"为什么"，而非"做了什么"）
4. `git add` 相关文件
5. `git commit` 创建提交

Commit message 规范：
- `feat: 新功能描述`
- `fix: 修复的问题描述`
- `refactor: 重构描述`
- `docs: 文档更新`
- `chore: 杂项维护`