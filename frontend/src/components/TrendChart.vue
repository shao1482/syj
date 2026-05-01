<template>
  <div ref="chartRef" :style="{ height: height, width: '100%' }"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: Object,
  title: { type: String, default: '' },
  height: { type: String, default: '400px' },
})

const chartRef = ref(null)
let chart = null

function renderChart() {
  if (!chartRef.value || !props.data) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  const series = props.data.series.map(s => ({
    name: s.name,
    type: 'line',
    data: s.data,
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
  }))
  chart.setOption({
    title: { text: props.title, left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0 },
    xAxis: { type: 'category', data: props.data.xData },
    yAxis: { type: 'value' },
    series,
    grid: { left: '10%', right: '10%', bottom: '15%', top: '15%' },
  })
}

onMounted(() => renderChart())
watch(() => props.data, () => renderChart(), { deep: true })
onUnmounted(() => { if (chart) chart.dispose() })
</script>