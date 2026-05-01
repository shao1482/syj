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
        <el-button type="info" @click="showConfig = true">预警规则配置</el-button>
      </div>

      <el-table :data="alerts" stripe>
        <el-table-column prop="patient_id" label="患者ID" width="80" />
        <el-table-column prop="alert_type" label="类型" width="120">
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

    <!-- 预警规则配置 -->
    <el-dialog v-model="showConfig" title="预警规则配置" width="800px">
      <el-tabs>
        <el-tab-pane label="固定阈值">
          <el-table :data="thresholdTable" stripe>
            <el-table-column prop="label" label="指标" width="100" />
            <el-table-column prop="low" label="低阈值" width="100" />
            <el-table-column prop="high" label="高阈值" width="100" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="联合预警规则">
          <el-table :data="combinedRules" stripe>
            <el-table-column prop="name" label="规则名称" width="150" />
            <el-table-column prop="message" label="预警信息" />
            <el-table-column prop="level" label="级别" width="100">
              <template #default="{ row }">
                <el-tag :type="levelType(row.level)">{{ levelLabel(row.level) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="其他参数">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="中医证候变化阈值">5 分</el-descriptions-item>
            <el-descriptions-item label="生活质量骤降比例">70%</el-descriptions-item>
            <el-descriptions-item label="随访逾期天数">30 天</el-descriptions-item>
            <el-descriptions-item label="动态阈值">基于患者历史均值+20%</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAlertStore } from '../stores/alert'
import api from '../api'

const alertStore = useAlertStore()
const filterLevel = ref('')
const filterStatus = ref('pending')
const alerts = ref([])
const showConfig = ref(false)
const alertConfig = ref(null)

const thresholdTable = computed(() => {
  if (!alertConfig.value?.lab_thresholds) return []
  return Object.entries(alertConfig.value.lab_thresholds).map(([k, v]) => ({
    label: v.label, low: v.low || '-', high: v.high || '-',
  }))
})

const combinedRules = computed(() => alertConfig.value?.combined_rules || [])

onMounted(async () => {
  loadAlerts()
  try { alertConfig.value = (await api.getAlertConfig()).data } catch {}
})

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
  const map = { lab: '检验', tcm: '证候', qol: '生活质量', followup: '随访', combined: '联合预警', tcm_lab: '证型关联' }
  return map[type] || type
}
</script>