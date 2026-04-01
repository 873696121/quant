<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>总资产</span>
          </template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>今日收益</span>
          </template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>持仓数量</span>
          </template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>运行策略</span>
          </template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
// Dashboard placeholder
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  padding: 20px 0;
  color: #409eff;
}
</style>
