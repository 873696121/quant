# 量化交易系统 - 云服务器部署指南

## 环境要求

| 项目 | 要求 |
|------|------|
| 系统 | CentOS 7+ / Ubuntu 20.04+ |
| CPU | 2 核+ |
| 内存 | 4GB+ |
| 磁盘 | 40GB+ |
| Docker | 20.10+ |
| Docker Compose | 2.0+ |

---

## 第一步：安装 Docker

### Ubuntu 系统

```bash
# 更新软件源
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加 Docker GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组（免 sudo）
sudo usermod -aG docker $USER
newgrp docker
```

### CentOS/RHEL 系统

```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
```

### 验证安装

```bash
docker --version
docker compose version
```

---

## 第二步：开放服务器端口

```bash
# Ubuntu (ufw)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 3000/tcp  # 前端
sudo ufw allow 8000/tcp  # 后端 API
sudo ufw allow 3306/tcp  # MySQL
sudo ufw allow 6379/tcp  # Redis
sudo ufw enable

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --permanent --add-port=6379/tcp
sudo firewall-cmd --reload

# 云服务器控制台也需要开放安全组规则
```

---

## 第三步：上传代码到服务器

```bash
# 在本地项目目录打包
cd /Users/huhong/PycharmProjects/quant
tar -czvf quant.tar.gz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' .

# 上传到服务器 (替换为你的服务器 IP)
scp quant.tar.gz root@115.190.198.148:/root/

# 在服务器上解压
ssh root@115.190.198.148
cd /root
tar -xzvf quant.tar.gz
```

---

## 第四步：配置环境变量

```bash
cd /root/quant

# 创建 .env 文件
cat > .env << 'EOF'
# 数据库配置
DB_PASSWORD=quant2026
DB_NAME=quant
DB_PORT=3306

# Redis 配置
REDIS_PORT=6379

# API 配置
API_PORT=8000
DEBUG=false

# 安全配置
SECRET_KEY=your-production-secret-key-change-this
EOF

# 修改文件权限
chmod 600 .env
```

---

## 第五步：启动服务

```bash
cd /root/quant

# 构建并启动所有服务
docker compose up -d --build

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
docker compose logs -f mysql
```

**预期输出：**
```
NAME                STATUS
quant_mysql         running (healthy)
quant_redis         running
quant_backend       running
quant_frontend      running
```

---

## 第六步：初始化数据库

```bash
# 等待 MySQL 就绪后，创建数据库
docker exec -it quant_mysql mysql -uroot -pquant2026 -e "CREATE DATABASE IF NOT EXISTS quant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行数据库迁移 (如果有)
docker exec -it quant_backend python -m alembic upgrade head
```

---

## 服务访问

| 服务 | 地址 |
|------|------|
| 前端 | http://115.190.198.148:3000 |
| 后端 API | http://115.190.198.148:8000 |
| API 文档 | http://115.190.198.148:8000/docs |
| Health 检查 | http://115.190.198.148:8000/health |

---

## 常用运维命令

```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart backend

# 停止所有服务
docker compose down

# 停止并删除数据卷（慎用，会清空数据）
docker compose down -v

# 重新构建并启动
docker compose up -d --build --force-recreate

# 查看资源使用
docker stats

# 进入容器内部
docker exec -it quant_backend /bin/bash
docker exec -it quant_mysql mysql -uroot -pquant2026

# 查看 MySQL 数据库
docker exec -it quant_mysql mysql -uroot -pquant2026 quant -e "SHOW TABLES;"

# 查看 Redis
docker exec -it quant_redis redis-cli ping
```

---

## 数据备份

```bash
# 备份 MySQL 数据
docker exec quant_mysql mysqldump -uroot -pquant2026 quant > backup_$(date +%Y%m%d).sql

# 备份 Redis 数据
docker exec quant_redis redis-cli SAVE
docker cp quant_redis:/data/dump.rdb ./redis_backup.rdb

# 备份整个项目
tar -czvf quant_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml backend/ frontend/
```

---

## 故障排查

### MySQL 连接失败
```bash
# 检查 MySQL 日志
docker compose logs mysql

# 检查 MySQL 容器状态
docker inspect quant_mysql

# 测试连接
docker exec -it quant_mysql mysql -uroot -pquant2026
```

### Backend 启动失败
```bash
# 查看后端日志
docker compose logs backend

# 检查依赖是否安装成功
docker exec -it quant_backend pip list

# 进入容器排查
docker exec -it quant_backend /bin/bash
```

### 前端无法访问
```bash
# 检查前端日志
docker compose logs frontend

# 检查容器是否正常运行
docker ps | grep frontend
```

---

## 安全加固（生产环境建议）

```bash
# 1. 修改 MySQL root 密码
docker exec -it quant_mysql mysql -uroot -pquant2026 -e "ALTER USER 'root'@'%' IDENTIFIED BY 'NewStrongPassword123!';" FLUSH PRIVILEGES;

# 2. 修改 .env 中的密码
vim .env

# 3. 重启服务使配置生效
docker compose down
docker compose up -d

# 4. 配置 Nginx 反向代理（可选）
# 5. 配置 SSL 证书（可选）
# 6. 定期更新 Docker 镜像
docker compose pull
docker compose up -d
```

---

## 快速部署脚本

创建 `deploy.sh`：

```bash
#!/bin/bash
set -e

echo "=== 部署量化交易系统 ==="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi

# 启动服务
echo "启动服务..."
docker compose up -d --build

# 等待 MySQL 就绪
echo "等待 MySQL 就绪..."
sleep 10

# 初始化数据库
echo "初始化数据库..."
docker exec -it quant_mysql mysql -uroot -pquant2026 -e "CREATE DATABASE IF NOT EXISTS quant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo ""
echo "=== 部署完成 ==="
echo "前端: http://$(curl -s ifconfig.me):3000"
echo "后端: http://$(curl -s ifconfig.me):8000"
echo "API文档: http://$(curl -s ifconfig.me):8000/docs"
```
