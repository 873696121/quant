<template>
  <div class="order-container">
    <h2>订单管理</h2>

    <el-card class="toolbar">
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="模式">
          <el-select v-model="queryForm.mode" placeholder="全部" clearable @change="loadOrders">
            <el-option label="回测" value="backtest" />
            <el-option label="模拟" value="paper" />
            <el-option label="实盘" value="live" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="全部" clearable @change="loadOrders">
            <el-option label="待成交" value="pending" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已成交" value="filled" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="showCreateDialog">下单</el-button>
          <el-button @click="loadOrders">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <span>订单列表</span>
      </template>
      <el-table :data="orders" v-loading="loading">
        <el-table-column prop="id" label="订单ID" width="80" />
        <el-table-column prop="symbol" label="股票代码" width="100" />
        <el-table-column prop="direction" label="方向" width="80">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'buy' ? 'danger' : 'success'">
              {{ row.direction === 'buy' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_type" label="类型" width="80">
          <template #default="{ row }">
            {{ row.order_type === 'market' ? '市价' : '限价' }}
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            {{ row.price ?? '市价' }}
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="委托量" width="100" />
        <el-table-column prop="filled_volume" label="成交量" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending' || row.status === 'submitted'"
              size="small"
              type="danger"
              @click="cancelOrder(row.id)"
            >
              撤单
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="下单" width="450px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="80px">
        <el-form-item label="股票代码" prop="symbol">
          <el-input v-model="form.symbol" placeholder="如: 000001.SZ" />
        </el-form-item>
        <el-form-item label="方向" prop="direction">
          <el-radio-group v-model="form.direction">
            <el-radio label="buy">买入</el-radio>
            <el-radio label="sell">卖出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="订单类型" prop="order_type">
          <el-select v-model="form.order_type" style="width: 100%">
            <el-option label="限价" value="limit" />
            <el-option label="市价" value="market" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price" v-if="form.order_type === 'limit'">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="数量" prop="volume">
          <el-input-number v-model="form.volume" :min="100" :step="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="模式" prop="mode">
          <el-select v-model="form.mode" style="width: 100%">
            <el-option label="回测" value="backtest" />
            <el-option label="模拟" value="paper" />
            <el-option label="实盘" value="live" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { orderApi } from '@/api/order'

const orders = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)

const formRef = ref(null)

const queryForm = reactive({
  mode: '',
  status: ''
})

const form = reactive({
  symbol: '',
  direction: 'buy',
  order_type: 'limit',
  price: null,
  volume: 100,
  mode: 'paper'
})

const formRules = {
  symbol: [
    { required: true, message: '请输入股票代码', trigger: 'blur' },
    { pattern: /^\d{6}\.(SH|SZ)$/, message: '格式如: 000001.SZ', trigger: 'blur' }
  ],
  direction: [{ required: true, message: '请选择方向', trigger: 'change' }],
  volume: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

onMounted(() => {
  loadOrders()
})

async function loadOrders() {
  loading.value = true
  try {
    const params = {}
    if (queryForm.mode) params.mode = queryForm.mode
    if (queryForm.status) params.status = queryForm.status
    orders.value = await orderApi.list(params)
  } catch (error) {
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  Object.assign(form, {
    symbol: '',
    direction: 'buy',
    order_type: 'limit',
    price: null,
    volume: 100,
    mode: 'paper'
  })
  dialogVisible.value = true
}

async function submitOrder() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await orderApi.create(form)
    ElMessage.success('下单成功')
    dialogVisible.value = false
    loadOrders()
  } catch (error) {
    ElMessage.error(error.message || '下单失败')
  } finally {
    submitting.value = false
  }
}

async function cancelOrder(id) {
  try {
    await orderApi.cancel(id)
    ElMessage.success('撤单成功')
    loadOrders()
  } catch (error) {
    ElMessage.error('撤单失败')
  }
}

function statusTagType(status) {
  const map = {
    pending: 'info',
    submitted: 'warning',
    filled: 'success',
    cancelled: 'info',
    rejected: 'danger'
  }
  return map[status] || 'info'
}

function statusText(status) {
  const map = {
    pending: '待成交',
    submitted: '已提交',
    filled: '已成交',
    cancelled: '已取消',
    rejected: '已拒绝'
  }
  return map[status] || status
}

function formatDate(dateStr) {
  if (!dateStr) return '--'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.order-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
}
</style>
