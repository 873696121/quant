<template>
  <div class="market-container">
    <h2>行情市场</h2>

    <el-card class="search-card">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索股票代码或名称"
        @keyup.enter="handleSearch"
        style="width: 300px; margin-right: 10px"
      >
        <template #append>
          <el-button @click="handleSearch" icon="Search" />
        </template>
      </el-input>
    </el-card>

    <el-card v-if="searchResults.length > 0" class="search-result">
      <template #header>
        <span>搜索结果</span>
      </template>
      <el-table :data="searchResults">
        <el-table-column prop="symbol" label="代码" width="120" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="price" label="现价" width="100">
          <template #default="{ row }">
            {{ row.price ?? '--' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="viewKline(row.symbol)">查看K线</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="kline-card" v-if="currentSymbol">
      <template #header>
        <span>{{ currentSymbol }} K线走势</span>
        <el-select v-model="klinePeriod" size="small" style="width: 120px; margin-left: 20px" @change="loadKline">
          <el-option label="日K" value="daily" />
          <el-option label="周K" value="weekly" />
          <el-option label="月K" value="monthly" />
        </el-select>
      </template>
      <div ref="klineChart" style="height: 400px"></div>
    </el-card>

    <el-card class="watchlist-card">
      <template #header>
        <span>自选股</span>
      </template>
      <el-table :data="watchlist" v-loading="loading">
        <el-table-column prop="symbol" label="代码" width="100" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="price" label="现价" width="100">
          <template #default="{ row }">
            <span :class="priceClass(row.change)">{{ row.price ?? '--' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="change" label="涨跌幅" width="100">
          <template #default="{ row }">
            <span :class="priceClass(row.change)">
              {{ row.change ? (row.change * 100).toFixed(2) + '%' : '--' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="120" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="viewKline(row.symbol)">K线</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { marketApi } from '@/api/market'
import * as echarts from 'echarts'

const searchKeyword = ref('')
const searchResults = ref([])
const watchlist = ref([])
const loading = ref(false)
const currentSymbol = ref('')
const klinePeriod = ref('daily')
const klineChart = ref(null)
let chartInstance = null

onMounted(() => {
  loadWatchlist()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})

async function handleSearch() {
  if (!searchKeyword.value.trim()) return
  try {
    searchResults.value = await marketApi.search(searchKeyword.value)
  } catch (error) {
    ElMessage.error('搜索失败')
  }
}

async function loadWatchlist() {
  loading.value = true
  try {
    const codes = ['000001', '600519', '600000']
    const quotes = await marketApi.getQuotes(codes)
    watchlist.value = quotes.map(q => ({
      symbol: q.symbol,
      name: q.name,
      price: q.price,
      change: q.change,
      volume: q.volume
    }))
  } catch (error) {
    console.error('加载自选股失败', error)
  } finally {
    loading.value = false
  }
}

async function viewKline(symbol) {
  currentSymbol.value = symbol
  await loadKline()
}

async function loadKline() {
  if (!currentSymbol.value) return
  try {
    const kline = await marketApi.getKline(currentSymbol.value, { period: klinePeriod.value })
    renderKline(kline)
  } catch (error) {
    ElMessage.error('加载K线失败')
  }
}

function renderKline(klineData) {
  if (!klineChart.value) return

  nextTick(() => {
    if (!chartInstance) {
      chartInstance = echarts.init(klineChart.value)
    }

    const dates = klineData.dates || []
    const opens = klineData.opens || []
    const highs = klineData.highs || []
    const lows = klineData.lows || []
    const closes = klineData.closes || []

    // K线数据格式: [open, close, low, high]
    const klineDataFormatted = opens.map((_, i) => [
      opens[i],
      closes[i],
      lows[i],
      highs[i]
    ])

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '10%'
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLabel: {
          formatter: (value) => value.substring(5)
        }
      },
      yAxis: {
        type: 'value',
        scale: true,
        splitLine: { show: true }
      },
      dataZoom: [
        { type: 'inside', start: 0, end: 100 },
        { type: 'slider', start: 0, end: 100 }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: klineDataFormatted,
          itemStyle: {
            color: '#ef5350',     // 上涨-红色
            color0: '#26a69a',   // 下跌-绿色
            borderColor: '#ef5350',
            borderColor0: '#26a69a'
          }
        }
      ]
    }

    chartInstance.setOption(option)
  })
}

function priceClass(change) {
  if (!change) return ''
  return change > 0 ? 'price-up' : change < 0 ? 'price-down' : ''
}
</script>

<style scoped>
.market-container {
  padding: 20px;
}

.search-card,
.search-result,
.kline-card,
.watchlist-card {
  margin-bottom: 20px;
}

.price-up {
  color: #f56c6c;
}

.price-down {
  color: #67c23a;
}
</style>
