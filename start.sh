#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}启动 Quant 量化交易系统...${NC}\n"

# 启动所有服务
docker compose up -d

echo -e "\n${GREEN}✅ 服务已启动${NC}"
echo -e "\n访问地址:"
echo -e "  前端:   http://localhost:3000"
echo -e "  后端:   http://localhost:8000"
echo -e "  API文档: http://localhost:8000/docs"
echo -e "\n管理命令:"
echo -e "  ${YELLOW}docker compose logs -f${NC}     查看日志"
echo -e "  ${YELLOW}docker compose down${NC}        停止服务"
echo -e "  ${YELLOW}docker compose restart${NC}     重启服务"
