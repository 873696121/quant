# Quant 量化交易系统

A quantitative trading research and execution platform for A-shares, supporting backtesting, paper trading, and live trading via QMT (MiniQMT).

## Features

- **Backtesting**: Historical data simulation with mock fees
- **Paper Trading**: Real-time quotes with simulated fill and real fees
- **Live Trading**: Real-time execution via QMT (MiniQMT) Python API
- **Market Data**: Real-time and historical data from akshare/tushare
- **Dashboard**: Visual monitoring of strategies and positions

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + Element Plus + ECharts + Pinia |
| Backend | Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) |
| Database | MySQL 8.0 |
| Cache | Redis 7 |
| Market Data | akshare, tushare |
| Live Trading | QMT (MiniQMT) Python API |

## Quick Start

### Setup

```bash
# Initialize environment and start services
./setup.sh

# Start all services via Docker Compose
./start.sh
```

### Development

**Backend:**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
alembic upgrade head
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
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

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── engine/       # Backtest engine
│   │   └── executors/    # Execution engines
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/       # Vue pages
│   │   ├── api/         # Axios modules
│   │   ├── stores/      # Pinia stores
│   │   └── router/      # Vue Router
│   └── Dockerfile
├── docker-compose.yml
├── setup.sh
└── start.sh
```

## License

MIT