<template>
  <div class="strategy-container">
    <h2>策略管理</h2>

    <el-card class="toolbar">
      <el-button type="primary" @click="showCreateDialog">创建策略</el-button>
    </el-card>

    <el-card class="strategy-list">
      <template #header>
        <span>策略列表</span>
      </template>
      <el-table :data="strategies" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="mode" label="模式" width="100">
          <template #default="{ row }">
            <el-tag :type="modeTagType(row.mode)">{{ row.mode }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="editStrategy(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteStrategy(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="策略名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" rows="3" placeholder="策略描述" />
        </el-form-item>
        <el-form-item label="模式" prop="mode">
          <el-select v-model="form.mode" placeholder="选择模式">
            <el-option label="回测" value="backtest" />
            <el-option label="模拟" value="paper" />
            <el-option label="实盘" value="live" />
          </el-select>
        </el-form-item>
        <el-form-item label="代码" prop="code">
          <el-input v-model="form.code" type="textarea" rows="10" placeholder="策略代码 (Python)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { strategyApi } from '@/api/strategy'

const strategies = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const currentId = ref(null)

const formRef = ref(null)

const form = reactive({
  name: '',
  description: '',
  mode: 'backtest',
  code: ''
})

const formRules = {
  name: [{ required: true, message: '请输入策略名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入策略代码', trigger: 'blur' }],
  mode: [{ required: true, message: '请选择模式', trigger: 'change' }]
}

const dialogTitle = computed => isEdit.value ? '编辑策略' : '创建策略'

onMounted(() => {
  loadStrategies()
})

async function loadStrategies() {
  loading.value = true
  try {
    strategies.value = await strategyApi.list()
  } catch (error) {
    ElMessage.error('加载策略失败')
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  isEdit.value = false
  currentId.value = null
  Object.assign(form, { name: '', description: '', mode: 'backtest', code: '' })
  dialogVisible.value = true
}

function editStrategy(row) {
  isEdit.value = true
  currentId.value = row.id
  Object.assign(form, {
    name: row.name,
    description: row.description || '',
    mode: row.mode,
    code: row.code
  })
  dialogVisible.value = true
}

async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await strategyApi.update(currentId.value, form)
      ElMessage.success('更新成功')
    } else {
      await strategyApi.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadStrategies()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function deleteStrategy(id) {
  try {
    await ElMessageBox.confirm('确定要删除该策略吗？', '提示', { type: 'warning' })
    await strategyApi.delete(id)
    ElMessage.success('删除成功')
    loadStrategies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function modeTagType(mode) {
  const map = { backtest: 'info', paper: 'warning', live: 'success' }
  return map[mode] || 'info'
}

function statusTagType(status) {
  const map = { active: 'success', stopped: 'info', error: 'danger' }
  return map[status] || 'info'
}

function formatDate(dateStr) {
  if (!dateStr) return '--'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.strategy-container {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
}
</style>
