<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div style="font-size: 24px; color: #409EFF;">{{ overview.total_patients }}</div>
            <div style="margin-top: 8px;">患者总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div style="font-size: 24px; color: #E6A23C;">{{ overview.pending_alerts }}</div>
            <div style="margin-top: 8px;">待处理预警</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div style="font-size: 24px; color: #F56C6C;">{{ overview.high_alerts }}</div>
            <div style="margin-top: 8px;">高危预警</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" @click="$router.push('/patients')" style="cursor: pointer;">
          <div style="text-align: center; color: #909399;">
            <div style="font-size: 24px;">查看全部患者</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card header="预警概览" style="margin-bottom: 20px;">
      <el-table :data="alerts" stripe max-height="400">
        <el-table-column prop="patient_id" label="患者ID" width="80" />
        <el-table-column prop="alert_type" label="类型" width="100" />
        <el-table-column prop="level" label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="levelType(row.level)">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="预警信息" />
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleResolve(row.id)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const overview = ref({ total_patients: 0, pending_alerts: 0, high_alerts: 0 })
const alerts = ref([])

onMounted(async () => {
  const res1 = await api.getOverview()
  overview.value = res1.data
  const res2 = await api.getAlerts({ status: 'pending' })
  alerts.value = res2.data
})

function levelType(level) {
  if (level === 'high') return 'danger'
  if (level === 'medium') return 'warning'
  return 'info'
}

async function handleResolve(id) {
  await api.resolveAlert(id)
  alerts.value = alerts.value.filter(a => a.id !== id)
  overview.value.pending_alerts--
}
</script>