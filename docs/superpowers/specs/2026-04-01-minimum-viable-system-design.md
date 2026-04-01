# 最小可用量化交易系统设计文档

## 1. 概述

**目标**：完成一个可前后端联调运行的最小系统
**完成度**：从当前 ~25% 提升至 ~60%
**范围**：认证、策略管理、订单管理、行情查询、Dashboard展示

## 2. 技术架构

### 2.1 技术栈
- 后端：Python 3.11 + FastAPI + SQLAlchemy (async)
- 前端：Vue 3 + Element Plus + Axios
- 数据库：MySQL 8.0 (Docker)
- 缓存：Redis (Docker)

### 2.2 项目结构

```
backend/
├── app/
│   ├── api/
│   │   └── routes.py          # 所有API路由
│   ├── core/
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库连接
│   │   └── security.py        # JWT认证
│   ├── models/
│   │   ├── base.py, user.py, strategy.py
│   │   ├── order.py, position.py, backtest.py
│   ├── schemas/               # Pydantic模型(新增)
│   │   ├── user.py, strategy.py, order.py, market.py
│   ├── services/              # 业务逻辑(新增)
│   │   ├── auth_service.py, strategy_service.py
│   │   ├── order_service.py, market_service.py
│   └── executors/             # 保留目录(暂不使用)
│   └── engine/                 # 保留目录(暂不使用)
└── requirements.txt

frontend/
├── src/
│   ├── views/
│   │   ├── Login.vue          # 登录页(新增)
│   │   ├── Dashboard.vue       # 完善
│   │   ├── Market.vue          # 完善
│   │   ├── Strategy.vue        # 完善
│   │   └── Order.vue           # 完善
│   ├── api/
│   │   └── index.js           # 已有时需要修改
│   └── router/
│       └── routes.js          # 添加登录路由
```

## 3. API 设计

### 3.1 认证模块 `/api/auth`

| 接口 | 方法 | 描述 | 请求体 |
|------|------|------|--------|
| `/api/auth/register` | POST | 注册 | `{username, password}` |
| `/api/auth/login` | POST | 登录 | `{username, password}` |
| `/api/auth/me` | GET | 当前用户 | - |

**登录响应**：
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {"id": 1, "username": "xxx"}
}
```

### 3.2 策略模块 `/api/strategies`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/strategies` | GET | 策略列表 |
| `/api/strategies` | POST | 创建策略 |
| `/api/strategies/{id}` | GET | 获取策略 |
| `/api/strategies/{id}` | PUT | 更新策略 |
| `/api/strategies/{id}` | DELETE | 删除策略 |

### 3.3 订单模块 `/api/orders`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/orders` | GET | 订单列表 |
| `/api/orders` | POST | 下单 |
| `/api/orders/{id}` | DELETE | 撤单 |
| `/api/orders/history` | GET | 历史订单 |

**下单请求**：`{symbol, direction, volume, price, mode}`

### 3.4 行情模块 `/api/market`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/market/quote` | GET | 行情数据 `?symbols=000001.SZ,600000.SH` |
| `/api/market/kline` | GET | K线数据 `?symbol=000001.SZ&period=daily` |
| `/api/market/search` | GET | 搜索股票 `?keyword=平安` |

### 3.5 Dashboard `/api/dashboard`

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/dashboard/summary` | GET | 账户概要 |
| `/api/dashboard/positions` | GET | 当前持仓 |

## 4. 数据库模型

### 4.1 现有模型（已实现）

- **User**: id, username, password_hash, created_at
- **Strategy**: id, user_id, name, code, config, mode, created_at
- **Order**: id, user_id, symbol, direction, volume, price, status, mode, created_at
- **Position**: id, user_id, symbol, volume, avg_cost, frozen_volume, updated_at
- **Backtest**: id, strategy_id, start_date, end_date, result_json, status, created_at

### 4.2 新增/修改

无需新增模型，利用现有模型即可。

## 5. 前端页面

### 5.1 登录页 (Login.vue) - 新增
- 用户名/密码输入
- 登录/注册切换
- 错误提示

### 5.2 Dashboard.vue - 完善
- 账户概览卡片（总资产、今日盈亏、持仓数）
- 持仓列表
- 当日订单列表

### 5.3 Strategy.vue - 完善
- 策略列表展示
- 创建策略按钮 → 打开对话框编辑
- 策略代码编辑器（textarea）
- 策略启停操作

### 5.4 Order.vue - 完善
- 当日订单列表
- 下单表单（股票代码、方向、数量、价格）
- 撤单按钮

### 5.5 Market.vue - 完善
- 自选股列表
- 实时行情展示
- K线图（简化版ECharts）
- 股票搜索添加自选

## 6. 服务层设计

### 6.1 auth_service.py
- `register_user(username, password)` → User
- `authenticate_user(username, password)` → User
- `create_access_token(user_id)` → JWT token

### 6.2 strategy_service.py
- `list_strategies(user_id)` → List[Strategy]
- `create_strategy(user_id, name, code, config)` → Strategy
- `update_strategy(id, data)` → Strategy
- `delete_strategy(id, user_id)` → bool

### 6.3 order_service.py
- `list_orders(user_id, mode)` → List[Order]
- `create_order(user_id, symbol, direction, volume, price, mode)` → Order
- `cancel_order(order_id, user_id)` → bool
- `simulate_fill(order)` → Order（模拟撮合）

### 6.4 market_service.py
- `get_quote(symbols)` → Dict[str, Quote]
- `get_kline(symbol, period)` → DataFrame
- `search_stock(keyword)` → List[StockInfo]
- 数据源：akshare

## 7. 认证方案

- 使用 PyJWT 生成 JWT token
- Token 有效期：7天
- 前端存储在 localStorage
- 请求头：`Authorization: Bearer <token>`
- 密码加密：bcrypt

## 8. 模拟撮合规则

下单后立即模拟成交：
- 买单：市价单按涨停价成交，限价单按指定价成交
- 卖单：市价单按跌停价成交，限价单按指定价成交
- 更新持仓表

## 9. 实施步骤

### 第一步：后端基础设施
1. 实现 `security.py` (JWT认证)
2. 实现 `schemas/` Pydantic模型
3. 实现 `services/` 服务层

### 第二步：后端API
1. 实现 `routes.py` 所有路由
2. 更新 `main.py` 注册路由

### 第三步：前端
1. 添加登录页
2. 完善各页面功能
3. 添加路由守卫

### 第四步：联调
1. Docker环境验证
2. 前后端联调测试

## 10. 暂不包含

- QMT 实盘对接
- 回测引擎
- 数据持久化到文件
- 复杂图表
- 权限管理（除本人数据）
