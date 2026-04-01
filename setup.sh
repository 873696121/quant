#!/bin/bash
set -e

echo "==================================="
echo "  Quant 量化交易系统 - 初始化脚本"
echo "==================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker 未安装${NC}"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}错误: Docker Compose 未安装${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker 检查通过${NC}"
}

# 检查 .env 文件
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}未找到 .env 文件，从 .env.example 创建...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}请编辑 .env 文件配置数据库密码等信息${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ .env 配置文件存在${NC}"
}

# 启动中间件
start_infra() {
    echo -e "\n${YELLOW}启动 MySQL 和 Redis...${NC}"
    docker compose up -d mysql redis
    echo -e "${GREEN}✓ 中间件启动完成${NC}"
}

# 等待 MySQL 就绪
wait_mysql() {
    echo -e "\n${YELLOW}等待 MySQL 就绪...${NC}"
    local max_attempts=30
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if docker exec quant_mysql mysqladmin ping -h localhost -u root -p"${DB_PASSWORD:-quant2026}" &> /dev/null; then
            echo -e "${GREEN}✓ MySQL 已就绪${NC}"
            return 0
        fi
        echo -e "  等待中... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e "${RED}错误: MySQL 启动超时${NC}"
    exit 1
}

# 主流程
main() {
    # 加载环境变量
    export $(grep -v '^#' .env | xargs) 2>/dev/null || true

    check_docker
    check_env
    start_infra
    wait_mysql

    echo -e "\n==================================="
    echo -e "${GREEN}✅ 初始化完成！${NC}"
    echo -e "==================================="
    echo -e "\n下一步:"
    echo -e "  1. 编辑 .env 配置文件"
    echo -e "  2. 运行 ${YELLOW}docker compose up -d${NC} 启动全部服务"
    echo -e "  3. 访问 http://localhost:3000"
    echo -e "\n管理命令:"
    echo -e "  ${YELLOW}docker compose logs -f${NC}     查看日志"
    echo -e "  ${YELLOW}docker compose down${NC}        停止服务"
    echo -e "  ${YELLOW}docker compose restart${NC}     重启服务"
}

main "$@"
