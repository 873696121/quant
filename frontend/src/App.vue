<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <h1>量化交易系统</h1>
      <el-menu
        mode="horizontal"
        :router="true"
        :default-active="$route.path"
        class="app-menu"
      >
        <el-menu-item index="/">Dashboard</el-menu-item>
        <el-menu-item index="/market">Market</el-menu-item>
        <el-menu-item index="/strategy">Strategy</el-menu-item>
        <el-menu-item index="/order">Order</el-menu-item>
      </el-menu>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
// Root component - layout handled by router-view
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #545c64;
  color: #fff;
}

.app-header h1 {
  margin: 0;
  font-size: 20px;
}

.app-menu {
  background-color: transparent;
  border: none;
}

.app-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
