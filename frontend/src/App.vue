<template>
  <el-container style="height: 100vh">
    <el-header style="background: #409EFF; color: #fff; display: flex; align-items: center; font-size: 18px; padding: 0 20px;">
      <span style="font-weight: bold;">脾胃消化患者临床数据监测系统</span>
      <el-badge v-if="alertCount > 0" :value="alertCount" style="margin-left: 20px;">
        <el-button size="small" type="warning" @click="$router.push('/alerts')">预警</el-button>
      </el-badge>
    </el-header>
    <el-container>
      <el-aside width="200px" style="background: #f5f5f5;">
        <el-menu :default-active="$route.path" router style="height: 100%;">
          <el-menu-item index="/patients">
            <span>患者列表</span>
          </el-menu-item>
          <el-menu-item index="/dashboard">
            <span>数据监测</span>
          </el-menu-item>
          <el-menu-item index="/alerts">
            <span>预警中心</span>
          </el-menu-item>
          <el-menu-item index="/reports">
            <span>数据分析</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from './api'

const alertCount = ref(0)

onMounted(async () => {
  try {
    const res = await api.getAlerts({ status: 'pending' })
    alertCount.value = res.data.length
  } catch { /* ignore */ }
})
</script>