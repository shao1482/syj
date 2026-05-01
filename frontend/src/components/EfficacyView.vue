<template>
  <el-card header="疗效评价">
    <div v-if="data">
      <!-- 中医证候疗效 -->
      <el-card v-if="data.tcm_efficacy" shadow="hover" style="margin-bottom: 16px;">
        <template #header>中医证候疗效评价</template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="初始积分">{{ data.tcm_efficacy.first_score }}</el-descriptions-item>
          <el-descriptions-item label="末次积分">{{ data.tcm_efficacy.last_score }}</el-descriptions-item>
          <el-descriptions-item label="积分变化率">
            <el-tag :type="data.tcm_efficacy.improvement ? 'success' : 'danger'">
              {{ data.tcm_efficacy.change_rate }}%
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div ref="tcmRadarRef" style="height: 300px; margin-top: 16px;"></div>
      </el-card>

      <!-- 实验室指标疗效 -->
      <el-card v-if="data.lab_efficacy" shadow="hover" style="margin-bottom: 16px;">
        <template #header>实验室指标疗效评价</template>
        <el-table :data="labTableData" stripe>
          <el-table-column prop="name" label="指标" width="100" />
          <el-table-column prop="first" label="初始值" width="100" />
          <el-table-column prop="last" label="末次值" width="100" />
          <el-table-column prop="change_rate" label="变化率">
            <template #default="{ row }">
              <el-tag :type="row.change_rate > 0 ? 'success' : 'danger'">{{ row.change_rate }}%</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 生活质量疗效 -->
      <el-card v-if="data.qol_efficacy" shadow="hover">
        <template #header>生活质量疗效评价</template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="初始评分">{{ data.qol_efficacy.first_score }}</el-descriptions-item>
          <el-descriptions-item label="末次评分">{{ data.qol_efficacy.last_score }}</el-descriptions-item>
          <el-descriptions-item label="变化率">
            <el-tag :type="data.qol_efficacy.change_rate > 0 ? 'success' : 'danger'">
              {{ data.qol_efficacy.change_rate }}%
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
    <el-empty v-else description="需要至少2条记录才能评价疗效" />
  </el-card>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const props = defineProps({ patientId: Number })
const data = ref(null)
const tcmRadarRef = ref(null)
let radarChart = null

const labNameMap = { alt: 'ALT', ast: 'AST', hgb: 'HGB', wbc: 'WBC', tbil: 'TBIL', alb: 'ALB' }
const labTableData = computed(() => {
  if (!data.value?.lab_efficacy) return []
  return Object.entries(data.value.lab_efficacy).map(([k, v]) => ({
    name: labNameMap[k] || k, first: v.first, last: v.last, change_rate: v.change_rate,
  }))
})

async function loadEfficacy() {
  try {
    const res = await api.getEfficacy(props.patientId)
    data.value = res.data
  } catch { data.value = null }
}

function renderRadar() {
  if (!data.value?.tcm_efficacy?.scores_timeline || !tcmRadarRef.value) return
  if (!radarChart) radarChart = echarts.init(tcmRadarRef.value)
  const timeline = data.value.tcm_efficacy.scores_timeline
  radarChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { data: timeline.map(t => t.date) },
    radar: {
      indicator: [
        { name: '积分', max: Math.max(...timeline.map(t => t.total)) * 1.2 || 50 },
      ],
    },
    series: [{
      type: 'radar',
      data: timeline.map(t => ({ name: t.date, value: [t.total] })),
    }],
  })
}

onMounted(() => loadEfficacy())
watch(data, () => renderRadar(), { deep: true })
onUnmounted(() => { if (radarChart) radarChart.dispose() })
</script>