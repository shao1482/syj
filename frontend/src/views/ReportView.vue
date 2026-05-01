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
        <el-button type="success" size="small" @click="runAgentAnalysis" :loading="agentLoading">多Agent协作分析</el-button>
        <el-button size="small" @click="runAiAnalysis" :loading="analysisLoading">原引擎分析</el-button>
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

      <!-- 多Agent协作分析结果 -->
      <div v-if="agentResult" style="margin-top: 20px;">
        <el-divider content-position="left">多Agent协作分析报告</el-divider>

        <!-- Agent流水线进度 -->
        <el-steps :active="agentResult.pipeline_steps?.length || 0" finish-status="success" align-center style="margin-bottom: 24px;">
          <el-step v-for="step in agentResult.pipeline_steps" :key="step.agent"
            :title="step.agent" :description="step.description"
            :status="step.status === 'success' ? 'success' : 'error'" />
        </el-steps>

        <!-- 1. 数据采集结果 -->
        <el-card shadow="hover" style="margin-bottom: 16px;" v-if="agentResult.collector?.rule_analysis">
          <template #header>
            <div style="display:flex; justify-content:space-between;">
              <span style="color:#909399; font-weight:bold;">数据采集Agent</span>
              <el-tag size="small" :type="agentResult.collector.confidence >= 0.8 ? 'success' : 'warning'">
                置信度 {{ (agentResult.collector.confidence * 100).toFixed(0) }}%
              </el-tag>
            </div>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="患者">{{ agentResult.collector.rule_analysis.patient_info?.name }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ agentResult.collector.rule_analysis.patient_info?.age }}岁</el-descriptions-item>
            <el-descriptions-item label="诊断">{{ agentResult.collector.rule_analysis.patient_info?.diagnosis }}</el-descriptions-item>
            <el-descriptions-item label="证候记录">{{ agentResult.collector.rule_analysis.completeness?.tcm_records }} 条</el-descriptions-item>
            <el-descriptions-item label="检验记录">{{ agentResult.collector.rule_analysis.completeness?.lab_records }} 条</el-descriptions-item>
            <el-descriptions-item label="生活质量">{{ agentResult.collector.rule_analysis.completeness?.qol_records }} 条</el-descriptions-item>
            <el-descriptions-item label="数据质量">{{ agentResult.collector.rule_analysis.completeness?.data_quality }}</el-descriptions-item>
            <el-descriptions-item label="缺失项">{{ agentResult.collector.rule_analysis.completeness?.missing_domains?.join(', ') || '无' }}</el-descriptions-item>
          </el-descriptions>
          <div v-if="agentResult.collector.model_analysis" style="margin-top: 12px; padding: 12px; background: #f0f9eb; border-radius: 4px;">
            <b>模型增强：</b>{{ agentResult.collector.model_analysis }}
          </div>
        </el-card>

        <!-- 2. 指标解析结果 -->
        <el-row :gutter="20" style="margin-bottom: 16px;" v-if="agentResult.analyzer?.rule_analysis">
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header><span style="color:#409EFF; font-weight:bold;">趋势分析</span></template>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item v-for="(t, key) in agentResult.analyzer.rule_analysis.trends" :key="key" :label="key">
                  {{ t.direction }} (斜率: {{ t.slope?.toFixed(2) }}, 最新值: {{ t.latest }})
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header><span style="color:#E6A23C; font-weight:bold;">异常指标</span></template>
              <el-tag v-for="a in agentResult.analyzer.rule_analysis.anomalies" :key="a.field"
                :type="a.severity === 'high' ? 'danger' : (a.severity === 'medium' ? 'warning' : 'info')"
                style="margin: 4px;" size="small">
                {{ a.label }}: {{ a.value }} (阈值{{ a.threshold }})
              </el-tag>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header><span style="color:#67C23A; font-weight:bold;">关联分析</span></template>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item v-for="c in agentResult.analyzer.rule_analysis.correlations" :key="c.pair" :label="c.pair">
                  r={{ c.correlation }} — {{ c.interpretation }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
        </el-row>

        <!-- 3. 风险评估结果 -->
        <el-card shadow="hover" style="margin-bottom: 16px;" v-if="agentResult.assessor?.rule_analysis">
          <template #header>
            <div style="display:flex; justify-content:space-between;">
              <span style="color:#F56C6C; font-weight:bold;">风险评估Agent</span>
              <el-tag :type="riskTagType" size="large">
                {{ agentResult.assessor.rule_analysis.risk_level_label }} ({{ agentResult.assessor.rule_analysis.risk_score }}分)
              </el-tag>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <h4>风险因素</h4>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item v-for="f in agentResult.assessor.rule_analysis.risk_factors" :key="f.factor" :label="f.domain">
                  {{ f.factor }} <el-tag size="small" type="warning">+{{ f.contribution }}分</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </el-col>
            <el-col :span="8">
              <h4>预警标记</h4>
              <el-alert v-for="flag in agentResult.assessor.rule_analysis.alert_flags" :key="flag.rule"
                :title="flag.rule" :description="flag.message"
                :type="flag.level === 'high' ? 'error' : 'warning'" show-icon :closable="false" style="margin-bottom: 8px;" />
              <p v-if="!agentResult.assessor.rule_analysis.alert_flags?.length" style="color:#909399;">无预警标记</p>
            </el-col>
            <el-col :span="8">
              <div v-if="agentResult.assessor.model_analysis" style="padding: 12px; background: #f0f9eb; border-radius: 4px;">
                <b>模型增强评估：</b>{{ agentResult.assessor.model_analysis }}
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 4. 干预建议结果 -->
        <el-row :gutter="20" style="margin-bottom: 16px;" v-if="agentResult.recommender?.rule_analysis">
          <el-col :span="6">
            <el-card shadow="hover">
              <template #header><span style="font-weight:bold;">随访计划</span></template>
              <p>{{ agentResult.recommender.rule_analysis.followup_plan?.frequency }}</p>
              <el-tag :type="riskTagType" size="small">{{ agentResult.recommender.rule_analysis.followup_plan?.risk_level }}风险</el-tag>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <template #header><span style="font-weight:bold;">复查计划</span></template>
              <ul><li v-for="r in agentResult.recommender.rule_analysis.recheck_plan" style="margin-bottom: 4px;">{{ r }}</li></ul>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <template #header><span style="color:#E6A23C; font-weight:bold;">治疗建议</span></template>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item v-for="s in agentResult.recommender.rule_analysis.treatment_suggestions" :key="s.suggestion" :label="s.type">
                  {{ s.suggestion }}<br/><small>{{ s.rationale }}</small>
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <template #header><span style="color:#67C23A; font-weight:bold;">生活建议</span></template>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item v-for="l in agentResult.recommender.rule_analysis.lifestyle_advice" :key="l.category" :label="l.category">
                  {{ l.advice }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
        </el-row>

        <!-- 预警建议 -->
        <el-card shadow="hover" style="margin-bottom: 16px;" v-if="agentResult.recommender?.rule_analysis?.alert_suggestions?.length">
          <template #header><span style="color:#F56C6C; font-weight:bold;">预警提示</span></template>
          <el-alert v-for="a in agentResult.recommender.rule_analysis.alert_suggestions" :key="a.message"
            :title="a.source" :description="a.message"
            :type="a.level === 'high' ? 'error' : 'warning'" show-icon :closable="false" style="margin-bottom: 8px;" />
        </el-card>

        <!-- 闭环验证 -->
        <el-card shadow="hover" v-if="agentResult.verification">
          <template #header>
            <div style="display:flex; justify-content:space-between;">
              <span style="font-weight:bold;">闭环验证</span>
              <el-tag :type="agentResult.verification.consistent ? 'success' : 'danger'">
                {{ agentResult.verification.consistent ? '验证通过' : '验证异常' }}
              </el-tag>
            </div>
          </template>
          <p>{{ agentResult.verification.summary }}</p>
          <ul v-if="agentResult.verification.gaps?.length">
            <li v-for="g in agentResult.verification.gaps" style="color: #F56C6C;">{{ g }}</li>
          </ul>
        </el-card>
      </div>

      <!-- 原引擎分析结果 -->
      <div v-if="analysisResult && !agentResult" style="margin-top: 20px;">
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
const agentResult = ref(null)
const agentLoading = ref(false)
const showModelConfig = ref(false)
const modelConfig = ref({ model_provider: 'template', ollama_url: 'http://localhost:11434', ollama_model: 'qwen2.5:7b' })

const riskTagType = computed(() => {
  const level = agentResult.value?.assessor?.rule_analysis?.risk_level
  return level === 'high' ? 'danger' : (level === 'medium' ? 'warning' : 'success')
})

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
  try { modelConfig.value = (await api.getAnalysisConfig()).data } catch {}
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

async function runAgentAnalysis() {
  if (!selectedPatientId.value) {
    ElMessage.warning('请先选择患者')
    return
  }
  agentLoading.value = true
  try {
    agentResult.value = (await api.agentAnalysis(selectedPatientId.value)).data
    ElMessage.success('多Agent协作分析完成')
  } catch (e) {
    ElMessage.error('分析失败: ' + (e.response?.data?.detail || e.message))
  }
  agentLoading.value = false
}

async function saveModelConfig() {
  try {
    await api.updateAnalysisConfig(modelConfig.value)
    ElMessage.success('模型配置已保存')
    showModelConfig.value = false
  } catch (e) {
    ElMessage.error('保存失败')
  }
}
</script>