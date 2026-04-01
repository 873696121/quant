#!/bin/bash
set -e

# ===========================================
# Quant 量化交易系统 - 云服务器部署脚本
# ===========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
CLOUD_HOST="115.190.198.148"
SSH_USER="root"
SSH_PORT="22"

echo -e "${YELLOW}=== Quant 量化交易系统 - 云服务器部署 ===${NC}\n"

# 检查本地 .env 文件
if [ ! -f .env ]; then
    echo -e "${RED}错误: .env 文件不存在${NC}"
    exit 1
fi

# 解析 CLOUD_HOST
CLOUD_HOST=$(grep "^CLOUD_HOST=" .env | cut -d'=' -f2)
if [ -z "$CLOUD_HOST" ] || [ "$CLOUD_HOST" = "你的云服务器IP" ]; then
    echo -e "${RED}错误: 请先在 .env 文件中配置正确的 CLOUD_HOST${NC}"
    exit 1
fi

echo -e "${GREEN}目标服务器: ${CLOUD_HOST}${NC}"

# 检查本地 Docker 和 docker compose
echo -e "\n${YELLOW}检查本地环境...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker 已安装${NC}"
else
    echo -e "${RED}错误: 本地 Docker 未安装${NC}"
    exit 1
fi

# 打包项目（排除不需要的目录）
echo -e "\n${YELLOW}打包项目文件...${NC}"
tar -czvf quant_deploy.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='docs' \
    --exclude='*.md' \
    backend/ frontend/ docker-compose.yml .env.example

echo -e "${GREEN}✓ 打包完成: quant_deploy.tar.gz${NC}"

# 上传到服务器
echo -e "\n${YELLOW}上传到服务器...${NC}"
sshpass -p "${SSH_PASSWORD}" scp -o StrictHostKeyChecking=no -P ${SSH_PORT} quant_deploy.tar.gz ${SSH_USER}@${CLOUD_HOST}:/root/

echo -e "${GREEN}✓ 上传完成${NC}"

# 在服务器上执行部署
echo -e "\n${YELLOW}在服务器上执行部署...${NC}"
sshpass -p "${SSH_PASSWORD}" ssh -o StrictHostKeyChecking=no -p ${SSH_PORT} ${SSH_USER}@${CLOUD_HOST} << 'ENDSSH'
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== 服务器端部署开始 ===${NC}\n"

# 解压项目
echo -e "${YELLOW}解压项目文件...${NC}"
cd /root
rm -rf quant 2>/dev/null || true
mkdir -p quant
tar -xzvf quant_deploy.tar.gz -C quant
cd quant
echo -e "${GREEN}✓ 解压完成${NC}"

# 检查 Docker
echo -e "\n${YELLOW}检查服务器 Docker 环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 服务器 Docker 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker 已安装: $(docker --version)${NC}"

if ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: 服务器 Docker Compose 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose 已安装${NC}"

# 创建 .env 文件
echo -e "\n${YELLOW}创建 .env 配置文件...${NC}"
cat > .env << 'ENVEOF'
# Quant 量化交易系统 - 云服务器部署配置
DEPLOYMENT=cloud
CLOUD_HOST=115.190.198.148
CLOUD_DB_HOST=115.190.198.148
CLOUD_DB_PORT=3306
CLOUD_DB_USER=root
CLOUD_DB_PASSWORD=Huhong@123
CLOUD_DB_NAME=quant
CLOUD_REDIS_HOST=115.190.198.148
CLOUD_REDIS_PORT=6379
CLOUD_REDIS_PASSWORD=
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=3306
LOCAL_DB_USER=root
LOCAL_DB_PASSWORD=quant2026
LOCAL_DB_NAME=quant
LOCAL_REDIS_HOST=localhost
LOCAL_REDIS_PORT=6379
LOCAL_REDIS_PASSWORD=
API_PORT=8000
FRONTEND_PORT=3000
DEBUG=false
SECRET_KEY=quant-2026-production-secret-key-change-this
DATA_SOURCE=akshare
TUSHARE_TOKEN=
ENVEOF
chmod 600 .env
echo -e "${GREEN}✓ .env 创建完成${NC}"

# 部署 MySQL 和 Redis
echo -e "\n${YELLOW}部署 MySQL 和 Redis...${NC}"
mkdir -p /opt/quant-services
cp docker-compose.yml /opt/quant-services/
cp .env /opt/quant-services/

cd /opt/quant-services
docker compose up -d mysql redis

# 等待 MySQL 就绪
echo -e "${YELLOW}等待 MySQL 就绪...${NC}"
for i in {1..30}; do
    if docker exec quant_mysql mysqladmin ping -h localhost -uroot -p"Huhong@123" &> /dev/null; then
        echo -e "${GREEN}✓ MySQL 已就绪${NC}"
        break
    fi
    echo "  等待中... ($i/30)"
    sleep 2
done

# 初始化数据库
echo -e "\n${YELLOW}初始化数据库...${NC}"
docker exec -it quant_mysql mysql -uroot -p"Huhong@123" -e \
    "CREATE DATABASE IF NOT EXISTS quant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" \
    2>/dev/null || echo "数据库可能已存在"

docker exec -it quant_mysql mysql -uroot -p"Huhong@123" -e \
    "ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Huhong@123'; FLUSH PRIVILEGES;" \
    2>/dev/null || echo "用户权限可能已配置"

# 启动应用服务
echo -e "\n${YELLOW}启动应用服务...${NC}"
docker compose up -d backend frontend

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo -e "\n${YELLOW}检查服务状态...${NC}"
docker compose ps

echo -e "\n==================================="
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "==================================="
echo -e "\n访问地址:"
echo -e "  前端:   http://${CLOUD_HOST}:3000"
echo -e "  后端:   http://${CLOUD_HOST}:8000"
echo -e "  API文档: http://${CLOUD_HOST}:8000/docs"
echo -e "\n管理命令:"
echo -e "  docker compose logs -f     查看日志"
echo -e "  docker compose ps          服务状态"
echo -e "  docker compose down         停止服务"
ENDSSH

# 检查部署结果
echo -e "\n${YELLOW}验证部署结果...${NC}"
if sshpass -p "${SSH_PASSWORD}" ssh -o StrictHostKeyChecking=no -p ${SSH_PORT} ${SSH_USER}@${CLOUD_HOST} "docker compose ps" 2>/dev/null | grep -q "quant_backend"; then
    echo -e "${GREEN}✓ Backend 服务运行中${NC}"
else
    echo -e "${YELLOW}⚠ Backend 服务状态待确认${NC}"
fi

# 清理本地临时文件
rm -f quant_deploy.tar.gz

echo -e "\n==================================="
echo -e "${GREEN}✅ 部署流程完成！${NC}"
echo -e "==================================="
echo -e "\n下一步:"
echo -e "  1. 访问 http://${CLOUD_HOST}:3000 验证前端"
echo -e "  2. 访问 http://${CLOUD_HOST}:8000/docs 验证后端 API"
echo -e "  3. 如有问题，运行 ${YELLOW}docker compose logs -f${NC} 查看日志"
