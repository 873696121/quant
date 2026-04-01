# 量化交易系统设计文档

## 1. 项目概述

**项目名称**：Quant 量化交易系统
**项目类型**：投研一体化平台（研究 + 回测 + 模拟盘 + 实盘）
**核心功能**：A股量化策略研究、回测验证、模拟交易、QMT实盘执行
**目标用户**：个人量化交易者

## 2. 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端 | Vue 3 + Element Plus + ECharts |
| 后端 | Python 3.11 + FastAPI |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis |
| 部署 | Docker + Docker Compose |
| 实盘接口 | QMT (MiniQMT) |

## 3. 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端 (Vue 3)                       │
│   个人控制台 │ 可视化研究 │ 回测图表 │ 策略编辑器           │
├─────────────────────────────────────────────────────────┤
│                     API 服务层 (FastAPI)                 │
│        任务调度 │ 策略管理 │ 实时监控 │ 回测运行            │
├─────────────────────────────────────────────────────────┤
│                     策略引擎层                           │
│         策略编写 │ 回测引擎 │ 模拟撮合 │ 信号生成           │
├─────────────────────────────────────────────────────────┤
│                     执行引擎层                           │
│              模拟执行 │ QMT实盘执行                        │
├─────────────────────────────────────────────────────────┤
│                     数据层                               │
│      数据采集 │ 存储 │ 预处理 │ 缓存 │ 实时行情             │
├─────────────────────────────────────────────────────────┤
│                  QMT 接口层                              │
│              QMT交易API (实盘专用)                        │
└─────────────────────────────────────────────────────────┘
                          ↓
              ┌───────────────────────┐
              │     Docker 部署       │
              │  MySQL │ Redis        │
              └───────────────────────┘
```

## 4. 功能模块

### 4.1 前端页面

| 页面 | 功能描述 |
|------|----------|
| Dashboard | 账户概览、持仓、实时盈亏、当日成交 |
| 行情监控 | 实时行情、自选股监控、K线图表 |
| 策略研究 | 因子编辑、回测配置、结果可视化 |
| 订单管理 | 当日委托、历史订单、撤单操作 |
| 策略编辑 | Python代码编辑器、语法高亮 |

### 4.2 执行模式

| 模式 | 数据源 | 订单执行 | 费用 |
|------|--------|----------|------|
| 回测 | 历史数据 | 模拟撮合 | 模拟费率 |
| 模拟盘 | 实时行情 | 模拟撮合 | 真实费率 |
| 实盘 | 实时行情 | QMT真单 | 真实费率 |

### 4.3 数据层

- **数据采集**：akshare / tushare 获取A股历史和实时数据
- **数据存储**：MySQL 存储K线、财务数据、订单记录
- **数据缓存**：Redis 缓存实时行情热点数据

### 4.4 QMT实盘对接

- 通过 QMT 的 Python API 连接
- 策略信号 → QMT 下单接口
- 用户本地需安装 QMT 客户端并登录

## 5. 数据库设计（ER概览）

```
users               # 用户表
├── id
├── username
├── api_key (QMT)
└── created_at

strategies          # 策略表
├── id
├── user_id
├── name
├── code (Python)
├── mode (backtest/paper/live)
└── created_at

backtests           # 回测记录表
├── id
├── strategy_id
├── start_date
├── end_date
├── result_json
└── created_at

orders              # 订单表
├── id
├── user_id
├── symbol
├── direction (buy/sell)
├── volume
├── price
├── status
├── mode
└── created_at

positions           # 持仓表
├── id
├── user_id
├── symbol
├── volume
├── avg_cost
└── updated_at
```

## 6. 核心接口（REST API）

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/strategies` | GET/POST | 策略列表/创建 |
| `/api/strategies/{id}` | GET/PUT/DELETE | 策略CRUD |
| `/api/backtest` | POST | 发起回测 |
| `/api/backtest/{id}` | GET | 回测结果 |
| `/api/orders` | GET/POST | 订单列表/下单 |
| `/api/orders/{id}` | DELETE | 撤单 |
| `/api/positions` | GET | 当前持仓 |
| `/api/market/quote` | GET | 行情数据 |
| `/api/market/kline` | GET | K线数据 |

## 7. 部署架构

```yaml
# docker-compose.yml 核心服务
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: quant

  redis:
    image: redis:7-alpine
```

## 8. 开发阶段规划

**第一阶段：框架搭建**
- 项目脚手架、Docker配置
- 数据库模型、迁移
- 基础API框架

**第二阶段：回测系统**
- 数据采集、存储
- 回测引擎实现
- 回测结果可视化

**第三阶段：模拟交易**
- 实时行情对接
- 模拟撮合引擎
- 订单管理

**第四阶段：QMT实盘**
- QMT API对接
- 实盘下单流程
- 信号推送机制

**第五阶段：前端完善**
- 各页面开发
- 图表集成
- 策略编辑器

## 9. 项目结构

```
quant/
├── backend/
│   ├── app/
│   │   ├── api/          # API路由
│   │   ├── core/         # 核心配置
│   │   ├── models/       # 数据库模型
│   │   ├── services/     # 业务逻辑
│   │   ├── engine/       # 策略/回测引擎
│   │   └──执行器/         # 模拟执行/QMT执行
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/        # 页面
│   │   ├── components/   # 组件
│   │   ├── api/          # 前端API调用
│   │   └── stores/       # 状态管理
│   ├── package.json
│   └── Dockerfile
├── docs/
│   └── specs/           # 设计文档
├── docker-compose.yml
└── README.md
```

## 10. 设计原则

1. **回测/实盘统一**：同一策略代码，通过配置切换执行模式
2. **分层解耦**：数据层、引擎层、执行层职责清晰
3. **Docker优先**：所有中间件本地Docker部署
4. **API先行**：前后端通过REST API通信
