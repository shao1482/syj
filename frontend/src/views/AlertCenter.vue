<template>
  <div>
    <el-card header="预警中心">
      <div style="display: flex; gap: 16px; margin-bottom: 16px;">
        <el-select v-model="filterLevel" placeholder="预警级别" clearable style="width: 120px;" size="small">
          <el-option label="高危" value="high" />
          <el-option label="中等" value="medium" />
          <el-option label="低级" value="low" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px;" size="small">
          <el-option label="待处理" value="pending" />
          <el-option label="已处理" value="resolved" />
        </el-select>
        <el-button size="small" @click="loadAlerts">筛选</el-button>
        <el-button size="small" type="info" @click="showConfig = true">预警规则配置</el-button>
      </div>

      <el-table :data="alerts" stripe>
        <el-table-column prop="patient_id" label="患者ID" width="80" />
        <el-table-column prop="alert_type" label="类型" width="120">
          <template #default="{ row }">{{ typeLabel(row.alert_type) }}</template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="80">
          <template #default="{ row }"><el-tag :type="levelType(row.level)">{{ levelLabel(row.level) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="message" label="预警信息" />
        <el-table-column prop="trigger_value" label="触发值" width="100" />
        <el-table-column prop="threshold" label="阈值" width="100" />
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : 'success'">{{ row.status === 'pending' ? '待处理' : '已处理' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" size="small" type="primary" @click="handleResolve(row.id)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 预警规则配置（可编辑） -->
    <el-dialog v-model="showConfig" title="预警规则配置" width="800px">
      <el-tabs>
        <el-tab-pane label="固定阈值">
          <el-table :data="editableThresholds" stripe>
            <el-table-column prop="label" label="指标" width="100" />
            <el-table-column label="低阈值" width="120">
              <template #default="{ row }"><el-input-number v-model="row.low" :precision="1" size="small" /></template>
            </el-table-column>
            <el-table-column label="高阈值" width="120">
              <template #default="{ row }"><el-input-number v-model="row.high" :precision="1" size="small" /></template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="联合预警规则">
          <el-table :data="editableRules" stripe>
            <el-table-column prop="name" label="规则名称" width="150" />
            <el-table-column prop="message" label="预警信息" />
            <el-table-column label="级别" width="100">
              <template #default="{ row }">
                <el-select v-model="row.level" size="small">
                  <el-option label="高危" value="high" /><el-option label="中等" value="medium" /><el-option label="低级" value="low" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="启用" width="80">
              <template #default="{ row }"><el-switch v-model="row.enabled" /></template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="其他参数">
          <el-form :model="editableParams" label-width="140px">
            <el-form-item label="中医证候变化阈值(分)"><el-input-number v-model="editableParams.tcm_change_threshold" :min="1" :max="20" /></el-form-item>
            <el-form-item label="生活质量骤降比例(%)"><el-input-number v-model="editableParams.qol_drop_ratio" :min="0.3" :max="1" :step="0.1" :precision="2" /></el-form-item>
            <el-form-item label="随访逾期天数"><el-input-number v-model="editableParams.followup_overdue_days" :min="7" :max="90" /></el-form-item>
            <el-form-item label="动态阈值倍率"><el-input-number v-model="editableParams.dynamic_threshold_ratio" :min="1" :max="2" :step="0.1" :precision="2" /></el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="showConfig = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAlertStore } from '../stores/alert'
import api from '../api'
import { ElMessage } from 'element-plus'

const alertStore = useAlertStore()
const filterLevel = ref('')
const filterStatus = ref('pending')
const alerts = ref([])
const showConfig = ref(false)
const editableThresholds = ref([])
const editableRules = ref([])
const editableParams = ref({ tcm_change_threshold: 5, qol_drop_ratio: 0.7, followup_overdue_days: 30, dynamic_threshold_ratio: 1.2 })

async function loadConfig() {
  const res = await api.getAlertConfig()
  const cfg = res.data
  editableThresholds.value = Object.entries(cfg.lab_thresholds || {}).map(([k, v]) => ({
    key: k, label: v.label, low: v.low, high: v.high,
  }))
  editableRules.value = (cfg.combined_rules || []).map(r => ({ ...r }))
  editableParams.value = {
    tcm_change_threshold: cfg.tcm_change_threshold || 5,
    qol_drop_ratio: cfg.qol_drop_ratio || 0.7,
    followup_overdue_days: cfg.followup_overdue_days || 30,
    dynamic_threshold_ratio: cfg.dynamic_threshold_ratio || 1.2,
  }
}

async function saveConfig() {
  const lab_thresholds = {}
  for (const t of editableThresholds.value) {
    lab_thresholds[t.key] = { label: t.label, low: t.low, high: t.high }
  }
  const config = {
    lab_thresholds,
    combined_rules: editableRules.value,
    tcm_change_threshold: editableParams.value.tcm_change_threshold,
    qol_drop_ratio: editableParams.value.qol_drop_ratio,
    followup_overdue_days: editableParams.value.followup_overdue_days,
    dynamic_threshold_ratio: editableParams.value.dynamic_threshold_ratio,
  }
  await api.updateAlertConfig(config)
  ElMessage.success('配置已保存')
  showConfig.value = false
}

onMounted(() => {
  loadAlerts()
  loadConfig()
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