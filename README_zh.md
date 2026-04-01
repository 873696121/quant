# Quant 量化交易系统

A 股量化交易研究与执行平台，支持回测、模拟交易和实盘交易（通过 QMT/MiniQMT）。

## 功能特性

- **回测**：历史数据模拟，支持模拟手续费
- **模拟交易**：实时行情，模拟成交，实盘手续费
- **实盘交易**：实时行情，QMT（MiniQMT）Python API 真实下单
- **行情数据**：akshare、tushare 提供实时和历史数据
- **可视化面板**：策略和持仓监控

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + ECharts + Pinia |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| 行情数据 | akshare, tushare |
| 实盘交易 | QMT (MiniQMT) Python API |

## 快速开始

### 环境初始化

```bash
# 初始化环境并启动服务
./setup.sh

# 通过 Docker Compose 启动所有服务
./start.sh
```

### 开发

**后端开发：**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
alembic upgrade head
```

**前端开发：**

```bash
cd frontend
npm install
npm run dev
```

## 架构图

```
┌─────────────────────────────────────────────────────┐
│                   前端 (Vue 3)                      │
│        仪表盘 │ 行情 │ 策略 │ 订单页面              │
├─────────────────────────────────────────────────────┤
│               API 服务层 (FastAPI)                   │
│      认证 │ 策略 │ 订单 │ 行情 │ 仪表盘            │
├─────────────────────────────────────────────────────┤
│                    引擎层                            │
│         回测引擎 │ 模拟执行引擎                      │
├─────────────────────────────────────────────────────┤
│                    数据层                            │
│   akshare/tushare → MySQL │ Redis 缓存 │ QMT API   │
└─────────────────────────────────────────────────────┘
```

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 配置、数据库、安全
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic schema
│   │   ├── services/     # 业务逻辑
│   │   ├── engine/       # 回测引擎
│   │   └── executors/    # 执行引擎
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/       # Vue 页面
│   │   ├── api/         # Axios 模块
│   │   ├── stores/      # Pinia 状态管理
│   │   └── router/      # Vue Router
│   └── Dockerfile
├── docker-compose.yml
├── setup.sh
└── start.sh
```

## License

MIT
