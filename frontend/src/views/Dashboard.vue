<template>
  <div class="dashboard">
    <h2>仪表盘</h2>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>总资产</span>
          </template>
          <div class="stat-value">{{ formatMoney(summary.total_asset) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>今日收益</span>
          </template>
          <div class="stat-value" :class="profitClass(summary.today_profit)">
            {{ formatProfit(summary.today_profit) }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>持仓数量</span>
          </template>
          <div class="stat-value">{{ summary.position_count || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>运行策略</span>
          </template>
          <div class="stat-value">{{ summary.strategy_count || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>持仓明细</span>
          </template>
          <el-table :data="positions" v-loading="loading">
            <el-table-column prop="symbol" label="股票" width="100" />
            <el-table-column prop="volume" label="持仓量" width="100" />
            <el-table-column prop="avg_cost" label="成本" width="100" />
            <el-table-column prop="profit" label="盈亏" width="100">
              <template #default="{ row }">
                <span :class="profitClass(row.profit)">{{ formatProfit(row.profit) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近订单</span>
          </template>
          <el-table :data="recentOrders">
            <el-table-column prop="symbol" label="股票" width="80" />
            <el-table-column prop="direction" label="方向" width="60">
              <template #default="{ row }">
                {{ row.direction === 'buy' ? '买' : '卖' }}
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="量" width="60" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/index'

const summary = ref({})
const positions = ref([])
const recentOrders = ref([])
const loading = ref(false)

onMounted(() => {
  loadDashboard()
})

async function loadDashboard() {
  loading.value = true
  try {
    const [summaryData, positionsData, ordersData] = await Promise.all([
      request.get('/dashboard/summary'),
      request.get('/dashboard/positions'),
      request.get('/orders', { params: { limit: 5 } })
    ])
    summary.value = summaryData
    positions.value = positionsData
    recentOrders.value = ordersData
  } catch (error) {
    ElMessage.error('加载仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

function formatProfit(value) {
  if (value === null || value === undefined) return '--'
  const sign = value >= 0 ? '+' : ''
  return sign + value.toFixed(2)
}

function formatMoney(value) {
  if (value == null) return '--'
  return value.toLocaleString('zh-CN', { style: 'currency', currency: 'CNY' })
}

function profitClass(value) {
  if (!value) return ''
  return value >= 0 ? 'profit-up' : 'profit-down'
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  padding: 10px 0;
  color: #409eff;
}

.profit-up {
  color: #f56c6c;  /* red for profit */
}

.profit-down {
  color: #67c23a;  /* green for loss */
}
</style>
