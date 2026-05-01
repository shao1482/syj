<template>
  <div v-if="patient">
    <el-page-header @back="$router.push('/patients')" :content="patient.name" style="margin-bottom: 16px;" />

    <el-descriptions title="患者基本信息" :column="3" border style="margin-bottom: 20px;">
      <el-descriptions-item label="姓名">{{ patient.name }}</el-descriptions-item>
      <el-descriptions-item label="性别">{{ patient.gender }}</el-descriptions-item>
      <el-descriptions-item label="年龄">{{ patient.age }}</el-descriptions-item>
      <el-descriptions-item label="电话">{{ patient.phone }}</el-descriptions-item>
      <el-descriptions-item label="入院日期">{{ patient.admission_date }}</el-descriptions-item>
      <el-descriptions-item label="西医诊断">{{ patient.diagnosis }}</el-descriptions-item>
      <el-descriptions-item label="中医诊断">{{ patient.tcm_diagnosis }}</el-descriptions-item>
      <el-descriptions-item label="备注">{{ patient.notes }}</el-descriptions-item>
    </el-descriptions>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="中医证候" name="tcm">
        <TcmScoreForm :patientId="patient.id" @saved="loadTcm" />
        <TrendChart v-if="clinical.tcmScores.length" :data="tcmChartData" title="中医证候总分趋势" />
        <el-table :data="clinical.tcmScores" stripe style="margin-top: 16px;">
          <el-table-column prop="record_date" label="日期" width="120" />
          <el-table-column prop="spleen_stomach_weak" label="脾胃虚弱" width="100" />
          <el-table-column prop="liver_stomachdisharmony" label="肝胃不和" width="100" />
          <el-table-column prop="spleen_stomach_dampheat" label="脾胃湿热" width="100" />
          <el-table-column prop="stomach_yin_deficiency" label="胃阴不足" width="100" />
          <el-table-column prop="tongue_score" label="舌象" width="80" />
          <el-table-column prop="pulse_score" label="脉象" width="80" />
          <el-table-column prop="total_score" label="总分" width="80" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="实验室检验" name="lab">
        <LabTestForm :patientId="patient.id" @saved="loadLab" />
        <TrendChart v-if="labChartData.length" :data="labChartData" title="检验指标趋势" />
        <el-table :data="clinical.labTests" stripe style="margin-top: 16px;">
          <el-table-column prop="record_date" label="日期" width="120" />
          <el-table-column prop="test_type" label="类型" width="120" />
          <el-table-column prop="wbc" label="WBC" width="80" />
          <el-table-column prop="hgb" label="HGB" width="80" />
          <el-table-column prop="alt" label="ALT" width="80" />
          <el-table-column prop="ast" label="AST" width="80" />
          <el-table-column prop="tbil" label="TBIL" width="80" />
          <el-table-column prop="alb" label="ALB" width="80" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="生活质量" name="qol">
        <QolForm :patientId="patient.id" @saved="loadQol" />
        <TrendChart v-if="clinical.qolRecords.length" :data="qolChartData" title="生活质量总分趋势" />
        <el-table :data="clinical.qolRecords" stripe style="margin-top: 16px;">
          <el-table-column prop="record_date" label="日期" width="120" />
          <el-table-column prop="nutrition_score" label="营养" width="80" />
          <el-table-column prop="pain_score" label="疼痛" width="80" />
          <el-table-column prop="sleep_score" label="睡眠" width="80" />
          <el-table-column prop="physical_function" label="生理功能" width="100" />
          <el-table-column prop="mental_health" label="心理" width="80" />
          <el-table-column prop="total_score" label="总分" width="80" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="治疗方案" name="treatment">
        <TreatmentForm :patientId="patient.id" @saved="loadTreatment" />
        <el-table :data="clinical.treatments" stripe style="margin-top: 16px;">
          <el-table-column prop="start_date" label="开始日期" width="120" />
          <el-table-column prop="end_date" label="结束日期" width="120" />
          <el-table-column prop="formula_name" label="方剂名称" />
          <el-table-column prop="western_medicine" label="西药" />
          <el-table-column prop="dosage" label="剂量" width="100" />
          <el-table-column prop="effect_rating" label="疗效评价" width="100" />
          <el-table-column prop="followup_note" label="随访记录" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePatientStore } from '../stores/patient'
import { useClinicalStore } from '../stores/clinical'
import TcmScoreForm from '../components/TcmScoreForm.vue'
import LabTestForm from '../components/LabTestForm.vue'
import QolForm from '../components/QolForm.vue'
import TreatmentForm from '../components/TreatmentForm.vue'
import TrendChart from '../components/TrendChart.vue'

const route = useRoute()
const store = usePatientStore()
const clinical = useClinicalStore()
const activeTab = ref('tcm')

const patient = computed(() => store.currentPatient)

const tcmChartData = computed(() => ({
  xData: clinical.tcmScores.map(s => s.record_date),
  series: [{ name: '总分', data: clinical.tcmScores.map(s => s.total_score) }],
}))

const labChartData = computed(() => {
  const blood = clinical.labTests.filter(t => t.test_type === 'blood_routine')
  const liver = clinical.labTests.filter(t => t.test_type === 'liver_func')
  const allDates = clinical.labTests.map(t => t.record_date)
  return {
    xData: allDates,
    series: [
      { name: 'HGB', data: clinical.labTests.map(t => t.hgb) },
      { name: 'ALT', data: clinical.labTests.map(t => t.alt) },
      { name: 'WBC', data: clinical.labTests.map(t => t.wbc) },
    ],
  }
})

const qolChartData = computed(() => ({
  xData: clinical.qolRecords.map(q => q.record_date),
  series: [{ name: '总分', data: clinical.qolRecords.map(q => q.total_score) }],
}))

onMounted(async () => {
  await store.fetchPatient(route.params.id)
  loadTcm()
})

function loadTcm() { clinical.fetchTcmScores(route.params.id) }
function loadLab() { clinical.fetchLabTests(route.params.id) }
function loadQol() { clinical.fetchQol(route.params.id) }
function loadTreatment() { clinical.fetchTreatments(route.params.id) }

watch(activeTab, (tab) => {
  if (tab === 'tcm') loadTcm()
  if (tab === 'lab') loadLab()
  if (tab === 'qol') loadQol()
  if (tab === 'treatment') loadTreatment()
})
</script>