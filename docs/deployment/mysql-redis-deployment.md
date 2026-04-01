# MySQL 和 Redis 独立部署指南

## 环境要求

| 项目 | 要求 |
|------|------|
| 系统 | CentOS 7+ / Ubuntu 20.04+ |
| Docker | 20.10+ |
| 端口 | 3306 (MySQL), 6379 (Redis) |

---

## 一键部署

```bash
# 创建部署目录
mkdir -p /opt/quant-services && cd /opt/quant-services

# 创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: quant_mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: quant2026
      MYSQL_DATABASE: quant
      TZ: Asia/Shanghai
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/conf:/etc/mysql/conf.d
    command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-pquant2026"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: quant_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./redis/conf:/usr/local/etc/redis
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mysql_data:
  redis_data:
EOF

# 创建配置目录
mkdir -p mysql/conf redis/conf

# 启动服务
docker compose up -d

# 等待服务就绪
sleep 15

# 验证服务
docker compose ps
```

---

## 详细配置

### MySQL 配置 (docker-compose.yml)

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 镜像 | mysql:8.0 | MySQL 8.0 |
| 端口 | 3306:3306 | 主机端口:容器端口 |
| 密码 | quant2026 | Root 密码 |
| 数据卷 | mysql_data:/var/lib/mysql | 持久化数据 |
| 字符集 | utf8mb4 | 支持 emoji |

### Redis 配置 (docker-compose.yml)

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 镜像 | redis:7-alpine | Redis 7 (Alpine 精简版) |
| 端口 | 6379:6379 | 主机端口:容器端口 |
| 持久化 | appendonly yes | AOF 持久化 |
| 数据卷 | redis_data:/data | 持久化数据 |

---

## 验证部署

```bash
# 检查容器状态
docker compose ps

# 预期输出:
# NAME         STATUS    PORTS
# quant_mysql  running   0.0.0.0:3306->3306/tcp
# quant_redis  running   0.0.0.0:6379->6379/tcp
```

### 测试 MySQL 连接

```bash
# 方式1: 使用 docker exec
docker exec -it quant_mysql mysql -uroot -pquant2026 -e "SELECT VERSION();"

# 方式2: 远程连接 (需安装 mysql-client)
mysql -h 115.190.198.148 -P 3306 -uroot -pquant2026 -e "SHOW DATABASES;"

# 创建数据库
docker exec -it quant_mysql mysql -uroot -pquant2026 -e \
  "CREATE DATABASE IF NOT EXISTS quant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 测试 Redis 连接

```bash
# 方式1: 使用 docker exec
docker exec -it quant_redis redis-cli ping
# 预期输出: PONG

# 方式2: 远程连接 (需安装 redis-cli)
redis-cli -h 115.190.198.148 -p 6379 ping
# 预期输出: PONG

# 测试读写
docker exec -it quant_redis redis-cli SET test "hello"
docker exec -it quant_redis redis-cli GET test
# 预期输出: hello
```

---

## 远程连接配置

### MySQL 远程访问

```bash
# 允许 root 远程登录
docker exec -it quant_mysql mysql -uroot -pquant2026 -e \
  "CREATE USER 'root'@'%' IDENTIFIED BY 'quant2026'; GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"

# 或修改现有用户
docker exec -it quant_mysql mysql -uroot -pquant2026 -e \
  "ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'quant2026'; FLUSH PRIVILEGES;"
```

### 开放防火墙

```bash
# Ubuntu (ufw)
sudo ufw allow 3306/tcp
sudo ufw allow 6379/tcp

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --permanent --add-port=6379/tcp
sudo firewall-cmd --reload

# 云服务器: 在控制台安全组开放 3306, 6379 端口
```

---

## 数据持久化

```bash
# 查看数据卷
docker volume ls | grep quant

# 备份 MySQL 数据
docker exec quant_mysql mysqldump -uroot -pquant2026 --all-databases > mysql_backup_$(date +%Y%m%d).sql

# 备份指定数据库
docker exec quant_mysql mysqldump -uroot -pquant2026 quant > quant_backup_$(date +%Y%m%d).sql

# 恢复 MySQL 数据
docker exec -i quant_mysql mysql -uroot -pquant2026 quant < quant_backup_20260401.sql

# 备份 Redis 数据
docker exec quant_redis redis-cli BGSAVE
docker cp quant_redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

---

## 常用运维命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart
docker compose restart mysql
docker compose restart redis

# 查看日志
docker compose logs -f
docker compose logs -f mysql
docker compose logs -f redis

# 进入容器
docker exec -it quant_mysql /bin/bash
docker exec -it quant_redis /bin/sh

# 查看资源使用
docker stats

# 更新镜像
docker compose pull
docker compose up -d
```

---

## 连接信息汇总

| 服务 | 主机 | 端口 | 用户 | 密码 | 数据库 |
|------|------|------|------|------|--------|
| MySQL | 115.190.198.148 | 3306 | root | quant2026 | quant |
| Redis | 115.190.198.148 | 6379 | - | - | - |

### Python 连接示例

```python
# MySQL (SQLAlchemy)
DATABASE_URL = "mysql+aiomysql://root:quant2026@115.190.198.148:3306/quant"

# Redis
REDIS_URL = "redis://:@115.190.198.148:6379/0"
```

### Node.js 连接示例

```javascript
// MySQL
const mysql = require('mysql2/promise');
const pool = mysql.createPool({
  host: '115.190.198.148',
  port: 3306,
  user: 'root',
  password: 'quant2026',
  database: 'quant'
});

// Redis
const redis = require('ioredis');
const client = new redis({
  host: '115.190.198.148',
  port: 6379
});
```

---

## 健康检查

```bash
# MySQL 健康检查
curl -s "http://localhost:3306" || echo "MySQL health check"

# Redis 健康检查
docker exec quant_redis redis-cli ping

# 综合检查脚本
#!/bin/bash
echo "=== 服务健康检查 ==="

echo -n "MySQL: "
docker exec quant_mysql mysqladmin ping -uroot -pquant2026 &>/dev/null && echo "OK" || echo "FAIL"

echo -n "Redis: "
docker exec quant_redis redis-cli ping &>/dev/null && echo "OK" || echo "FAIL"

echo "=== 检查完成 ==="
```
