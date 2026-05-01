<template>
  <el-card header="临床时间轴" style="margin-top: 16px;">
    <el-timeline>
      <el-timeline-item v-for="event in events" :key="event.date + event.type + event.title"
        :timestamp="event.date" :color="typeColor(event.type)" placement="top">
        <el-card shadow="hover" style="padding: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <el-tag :color="typeColor(event.type)" style="color: #fff; border: none;" size="small">{{ event.type }}</el-tag>
              <span style="margin-left: 8px; font-weight: bold;">{{ event.title }}</span>
            </div>
          </div>
          <p style="margin-top: 4px; color: #606266; font-size: 13px;">{{ event.detail }}</p>
        </el-card>
      </el-timeline-item>
    </el-timeline>
    <el-empty v-if="!events.length" description="暂无临床事件" />
  </el-card>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api'

const props = defineProps({ patientId: Number })
const events = ref([])

async function loadTimeline() {
  if (!props.patientId) return
  try {
    const res = await api.getTimeline(props.patientId)
    events.value = res.data.events || []
  } catch { events.value = [] }
}

onMounted(() => loadTimeline())
watch(() => props.patientId, () => loadTimeline())

function typeColor(type) {
  const map = {
    '入院': '#409EFF', '出院': '#909399', '中医证候': '#E6A23C',
    '实验室检验': '#F56C6C', '生活质量': '#67C23A', '治疗方案': '#6C63FF',
    '预警': '#FF4D4F', '随访': '#1890FF',
  }
  return map[type] || '#909399'
}
</script>