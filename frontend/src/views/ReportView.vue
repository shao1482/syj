<template>
  <div>
    <el-card header="数据分析报表">
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6"><el-statistic title="患者总数" :value="overview.total_patients" /></el-col>
        <el-col :span="6"><el-statistic title="待处理预警" :value="overview.pending_alerts" /></el-col>
        <el-col :span="6"><el-statistic title="高危预警" :value="overview.high_alerts" /></el-col>
      </el-row>

      <el-divider />

      <h3>单患者趋势分析</h3>
      <div style="display: flex; gap: 16px; margin-bottom: 16px;">
        <el-select v-model="selectedPatientId" placeholder="选择患者" @change="loadTrend" style="width: 180px;" size="small">
          <el-option v-for="p in patients" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-button type="success" size="small" @click="runAiAnalysis" :loading="analysisLoading">智能分析</el-button>
        <el-button size="small" @click="showModelConfig = true">模型配置</el-button>
      </div>

      <el-row :gutter="20" v-if="trend">
        <el-col :span="8">
          <el-card header="中医证候总分趋势"><TrendChart :data="tcmTrendData" title="" height="300px" /></el-card>
        </el-col>
        <el-col :span="8">
          <el-card header="生活质量总分趋势"><TrendChart :data="qolTrendData" title="" height="300px" /></el-card>
        </el-col>
        <el-col :span="8">
          <el-card header="检验指标趋势"><TrendChart :data="labTrendData" title="" height="300px" /></el-card>
        </el-col>
      </el-row>

      <!-- AI智能分析结果 -->
      <div v-if="analysisResult" style="margin-top: 20px;">
        <el-divider content-position="left">智能分析报告 — {{ analysisResult.patient_name }}</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header><span style="color: #E6A23C;">中医辨证分析</span></template>
              <p><b>{{ analysisResult.tcm_analysis?.summary }}</b></p>
              <ul><li v-for="d in analysisResult.tcm_analysis?.details">{{ d }}</li></ul>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header><span style="color: #409EFF;">检验指标分析</span></template>
              <p><b>{{ analysisResult.lab_analysis?.summary }}</b></p>
              <ul><li v-for="d in analysisResult.lab_analysis?.details">{{ d }}</li></ul>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header><span style="color: #67C23A;">生活质量分析</span></template>
              <p><b>{{ analysisResult.qol_analysis?.summary }}</b></p>
              <ul><li v-for="d in analysisResult.qol_analysis?.details">{{ d }}</li></ul>
            </el-card>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 16px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header><span style="color: #F56C6C;">干预建议</span></template>
              <ul><li v-for="r in analysisResult.recommendations" style="margin-bottom: 8px;">{{ r }}</li></ul>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>数据概览</template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="诊断">{{ analysisResult.diagnosis }}</el-descriptions-item>
                <el-descriptions-item label="中医诊断">{{ analysisResult.tcm_diagnosis }}</el-descriptions-item>
                <el-descriptions-item label="证候记录">{{ analysisResult.data_summary?.tcm_records }} 条</el-descriptions-item>
                <el-descriptions-item label="检验记录">{{ analysisResult.data_summary?.lab_records }} 条</el-descriptions-item>
                <el-descriptions-item label="待处理预警">{{ analysisResult.pending_alerts }} 条</el-descriptions-item>
                <el-descriptions-item label="治疗记录">{{ analysisResult.data_summary?.treatment_records }} 条</el-descriptions-item>
              </el-descriptions>
              <div v-if="analysisResult.ollama_enhanced" style="margin-top: 16px; padding: 12px; background: #f0f9eb; border-radius: 4px;">
                <b>Ollama增强分析：</b><p>{{ analysisResult.ollama_enhanced }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 模型配置对话框 -->
    <el-dialog v-model="showModelConfig" title="分析模型配置" width="500px">
      <el-form :model="modelConfig" label-width="120px">
        <el-form-item label="分析引擎">
          <el-select v-model="modelConfig.model_provider">
            <el-option label="本地模板引擎（默认）" value="template" />
            <el-option label="本地Ollama模型" value="ollama" />
          </el-select>
        </el-form-item>
        <el-form-item label="Ollama地址" v-if="modelConfig.model_provider === 'ollama'">
          <el-input v-model="modelConfig.ollama_url" placeholder="http://localhost:11434" />
        </el-form-item>
        <el-form-item label="模型名称" v-if="modelConfig.model_provider === 'ollama'">
          <el-input v-model="modelConfig.ollama_model" placeholder="qwen2.5:7b" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showModelConfig = false">取消</el-button>
        <el-button type="primary" @click="saveModelConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'
import TrendChart from '../components/TrendChart.vue'

const overview = ref({ total_patients: 0, pending_alerts: 0, high_alerts: 0 })
const patients = ref([])
const selectedPatientId = ref(null)
const trend = ref(null)
const analysisResult = ref(null)
const analysisLoading = ref(false)
const showModelConfig = ref(false)
const modelConfig = ref({ model_provider: 'template', ollama_url: 'http://localhost:11434', ollama_model: 'qwen2.5:7b' })

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
  overview.value = (await api.getOverview()).data
  patients.value = (await api.getPatients()).data
  try { modelConfig.value = (await api.request.get('/reports/analysis-config')).data } catch {}
})

async function loadTrend() {
  if (!selectedPatientId.value) return
  trend.value = (await api.getTrend(selectedPatientId.value)).data
}

async function runAiAnalysis() {
  if (!selectedPatientId.value) {
    ElMessage.warning('请先选择患者')
    return
  }
  analysisLoading.value = true
  try {
    analysisResult.value = (await api.aiAnalysis(selectedPatientId.value)).data
    ElMessage.success('分析完成')
  } catch (e) {
    ElMessage.error('分析失败: ' + (e.response?.data?.detail || e.message))
  }
  analysisLoading.value = false
}

async function saveModelConfig() {
  try {
    await api.request.put('/reports/analysis-config', modelConfig.value)
    ElMessage.success('模型配置已保存')
    showModelConfig.value = false
  } catch (e) {
    ElMessage.error('保存失败')
  }
}
</script>