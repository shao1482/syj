<template>
  <div>
    <el-card header="数据分析报表">
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-statistic title="患者总数" :value="overview.total_patients" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="待处理预警" :value="overview.pending_alerts" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="高危预警" :value="overview.high_alerts" />
        </el-col>
      </el-row>

      <el-divider />

      <h3>单患者趋势分析</h3>
      <el-select v-model="selectedPatientId" placeholder="选择患者" @change="loadTrend" style="width: 200px; margin-bottom: 16px;">
        <el-option v-for="p in patients" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>

      <el-row :gutter="20" v-if="trend">
        <el-col :span="8">
          <el-card header="中医证候总分趋势">
            <TrendChart :data="tcmTrendData" title="" height="300px" />
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card header="生活质量总分趋势">
            <TrendChart :data="qolTrendData" title="" height="300px" />
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card header="检验指标趋势">
            <TrendChart :data="labTrendData" title="" height="300px" />
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import TrendChart from '../components/TrendChart.vue'

const overview = ref({ total_patients: 0, pending_alerts: 0, high_alerts: 0 })
const patients = ref([])
const selectedPatientId = ref(null)
const trend = ref(null)

const tcmTrendData = computed(() => ({
  xData: trend.value?.tcm_scores?.map(s => s.date) || [],
  series: [{ name: '总分', data: trend.value?.tcm_scores?.map(s => s.total_score) || [] }],
}))

const qolTrendData = computed(() => ({
  xData: trend.value?.qol?.map(q => q.date) || [],
  series: [{ name: '总分', data: trend.value?.qol?.map(q => q.total_score) || [] }],
}))

const labTrendData = computed(() => ({
  xData: trend.value?.lab_tests?.map(t => t.date) || [],
  series: [
    { name: 'ALT', data: trend.value?.lab_tests?.map(t => t.alt || null) || [] },
    { name: 'HGB', data: trend.value?.lab_tests?.map(t => t.hgb || null) || [] },
  ],
}))

onMounted(async () => {
  const res1 = await api.getOverview()
  overview.value = res1.data
  const res2 = await api.getPatients()
  patients.value = res2.data
})

async function loadTrend() {
  if (!selectedPatientId.value) return
  const res = await api.getTrend(selectedPatientId.value)
  trend.value = res.data
}
</script>