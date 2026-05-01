<template>
  <div>
    <el-card header="预警中心">
      <div style="display: flex; gap: 16px; margin-bottom: 16px;">
        <el-select v-model="filterLevel" placeholder="预警级别" clearable style="width: 120px;">
          <el-option label="高危" value="high" />
          <el-option label="中等" value="medium" />
          <el-option label="低级" value="low" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px;">
          <el-option label="待处理" value="pending" />
          <el-option label="已处理" value="resolved" />
        </el-select>
        <el-button @click="loadAlerts">筛选</el-button>
      </div>

      <el-table :data="alerts" stripe>
        <el-table-column prop="patient_id" label="患者ID" width="80" />
        <el-table-column prop="alert_type" label="类型" width="100">
          <template #default="{ row }">
            {{ typeLabel(row.alert_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="levelType(row.level)">{{ levelLabel(row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="预警信息" />
        <el-table-column prop="trigger_value" label="触发值" width="100" />
        <el-table-column prop="threshold" label="阈值" width="100" />
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : 'success'">
              {{ row.status === 'pending' ? '待处理' : '已处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" size="small" type="primary" @click="handleResolve(row.id)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAlertStore } from '../stores/alert'

const alertStore = useAlertStore()
const filterLevel = ref('')
const filterStatus = ref('pending')
const alerts = ref([])

onMounted(() => loadAlerts())

async function loadAlerts() {
  const params = {}
  if (filterLevel.value) params.level = filterLevel.value
  if (filterStatus.value) params.status = filterStatus.value
  await alertStore.fetchAlerts(params)
  alerts.value = alertStore.alerts
}

async function handleResolve(id) {
  await alertStore.resolveAlert(id)
  loadAlerts()
}

function levelType(level) {
  if (level === 'high') return 'danger'
  if (level === 'medium') return 'warning'
  return 'info'
}
function levelLabel(level) {
  const map = { high: '高危', medium: '中等', low: '低级' }
  return map[level] || level
}
function typeLabel(type) {
  const map = { lab: '检验', tcm: '证候', qol: '生活质量', followup: '随访' }
  return map[type] || type
}
</script>