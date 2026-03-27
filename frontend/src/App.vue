<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <el-header height="60px" class="app-header">
      <div class="logo">AI 视觉智能监控系统</div>
      <el-menu :default-active="activeMenu" mode="horizontal" background-color="#1f2329" text-color="#fff" active-text-color="#409EFF">
        <el-menu-item index="sites">站点管理</el-menu-item>
        <el-menu-item index="about">关于系统</el-menu-item>
      </el-menu>
    </el-header>
    
    <!-- 主内容区 -->
    <el-main class="app-main">
      <router-view></router-view>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeMenu = ref('sites')
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #1f2329;
  color: #fff;
  padding: 0 20px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.app-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>