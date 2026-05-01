<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="4">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div style="font-size: 24px; color: #409EFF;">{{ overview.total_patients }}</div>
            <div style="margin-top: 8px;">患者总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div style="font-size: 24px; color: #E6A23C;">{{ overview.pending_alerts }}</div>
            <div style="margin-top: 8px;">待处理预警</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div style="font-size: 24px; color: #F56C6C;">{{ overview.high_alerts }}</div>
            <div style="margin-top: 8px;">高危预警</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div style="font-size: 24px; color: #F56C6C;">{{ overview.high_risk_patients || 0 }}</div>
            <div style="margin-top: 8px;">高危患者数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div style="font-size: 24px; color: #E6A23C;">{{ overview.overdue_followups || 0 }}</div>
            <div style="margin-top: 8px;">随访逾期数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" @click="$router.push('/patients')" style="cursor: pointer;">
          <div style="text-align: center; color: #909399;">
            <div style="font-size: 24px;">查看全部患者</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card header="预警概览">
          <el-table :data="alerts" stripe max-height="400">
            <el-table-column prop="patient_id" label="患者ID" width="80" />
            <el-table-column prop="alert_type" label="类型" width="100">
              <template #default="{ row }">{{ typeLabel(row.alert_type) }}</template>
            </el-table-column>
            <el-table-column prop="level" label="级别" width="80">
              <template #default="{ row }"><el-tag :type="levelType(row.level)" size="small">{{ levelLabel(row.level) }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="message" label="预警信息" show-overflow-tooltip />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" size="small" type="primary" @click="handleResolve(row.id)">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card header="随访提醒">
          <el-table :data="reminders" stripe max-height="400">
            <el-table-column prop="patient_id" label="患者ID" width="80" />
            <el-table-column prop="plan_date" label="计划日期" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'overdue' ? 'danger' : 'warning'" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="内容" show-overflow-tooltip />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button size="small" @click="$router.push(`/patients/${row.patient_id}`)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card header="证型分布">
          <div ref="syndromeChartRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const overview = ref({ total_patients: 0, pending_alerts: 0, high_alerts: 0, high_risk_patients: 0, overdue_followups: 0 })
const alerts = ref([])
const reminders = ref([])
const syndromeChartRef = ref(null)
let syndromeChart = null

onMounted(async () => {
  const res1 = await api.getOverview()
  overview.value = res1.data
  const res2 = await api.getAlerts({ status: 'pending' })
  alerts.value = res2.data
  try {
    const res3 = await api.getFollowupReminders()
    reminders.value = res3.data
  } catch {}
  // 证型分布
  const patients = (await api.getPatients()).data
  let syndromeCount = { '脾胃虚弱': 0, '肝胃不和': 0, '脾胃湿热': 0, '胃阴不足': 0 }
  for (const p of patients) {
    if (p.tcm_diagnosis) {
      for (const key of Object.keys(syndromeCount)) {
        if (p.tcm_diagnosis.includes(key)) syndromeCount[key]++
      }
    }
  }
  if (syndromeChartRef.value) {
    syndromeChart = echarts.init(syndromeChartRef.value)
    syndromeChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        data: Object.entries(syndromeCount).map(([k, v]) => ({ name: k, value: v })),
        label: { formatter: '{b}: {c}' },
      }],
    })
  }
})

onUnmounted(() => { if (syndromeChart) syndromeChart.dispose() })

async function handleResolve(id) {
  await api.resolveAlert(id)
  alerts.value = alerts.value.filter(a => a.id !== id)
  overview.value.pending_alerts--
}

function levelType(level) {
  if (level === 'high') return 'danger'
  if (level === 'medium') return 'warning'
  return 'info'
}
function levelLabel(level) {
  return { high: '高危', medium: '中等', low: '低级' }[level] || level
}
function typeLabel(type) {
  return { lab: '检验', tcm: '证候', qol: '生活质量', followup: '随访', combined: '联合预警', tcm_lab: '证型关联' }[type] || type
}
function statusLabel(status) {
  return { planned: '计划中', completed: '已完成', overdue: '已逾期', cancelled: '已取消' }[status] || status
}
</script>