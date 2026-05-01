<template>
  <div v-if="patient">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <el-page-header @back="$router.push('/patients')" :content="patient.name" />
      <div>
        <el-button type="success" @click="exportPdf">导出PDF</el-button>
        <el-button @click="exportLabExcel">导出检验Excel</el-button>
        <el-button type="warning" @click="openEditDialog">编辑</el-button>
      </div>
    </div>

    <el-descriptions title="患者基本信息" :column="4" border style="margin-bottom: 20px;">
      <el-descriptions-item label="姓名">{{ patient.name }}</el-descriptions-item>
      <el-descriptions-item label="性别">{{ patient.gender }}</el-descriptions-item>
      <el-descriptions-item label="年龄">{{ patient.age }}</el-descriptions-item>
      <el-descriptions-item label="门诊号">{{ patient.patient_no || '未填写' }}</el-descriptions-item>
      <el-descriptions-item label="住院号">{{ patient.inpatient_no || '未填写' }}</el-descriptions-item>
      <el-descriptions-item label="床号">{{ patient.bed_no || '未填写' }}</el-descriptions-item>
      <el-descriptions-item label="科室">{{ patient.department || '未填写' }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="statusType(patient.status)">{{ patient.status || '在院' }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="风险等级">
        <el-tag v-if="patient.risk_level" :type="riskType(patient.risk_level)">{{ riskLabel(patient.risk_level) }}</el-tag>
        <span v-else style="color:#909399;">未评估</span>
      </el-descriptions-item>
      <el-descriptions-item label="责任医生">{{ patient.responsible_doctor || '未填写' }}</el-descriptions-item>
      <el-descriptions-item label="责任护士">{{ patient.responsible_nurse || '未填写' }}</el-descriptions-item>
      <el-descriptions-item label="入院日期">{{ patient.admission_date }}</el-descriptions-item>
      <el-descriptions-item label="西医诊断">{{ patient.diagnosis }}</el-descriptions-item>
      <el-descriptions-item label="中医诊断">{{ patient.tcm_diagnosis }}</el-descriptions-item>
      <el-descriptions-item label="电话">{{ patient.phone }}</el-descriptions-item>
      <el-descriptions-item label="过敏史">{{ patient.allergy_history || '无' }}</el-descriptions-item>
      <el-descriptions-item label="既往史">{{ patient.past_history || '无' }}</el-descriptions-item>
      <el-descriptions-item label="家族史">{{ patient.family_history || '无' }}</el-descriptions-item>
      <el-descriptions-item label="入院评估">{{ patient.admission_assessment || '未填写' }}</el-descriptions-item>
      <el-descriptions-item label="出院小结">{{ patient.discharge_summary || '未填写' }}</el-descriptions-item>
      <el-descriptions-item label="备注">{{ patient.notes || '无' }}</el-descriptions-item>
    </el-descriptions>

    <!-- 编辑患者对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑患者信息" width="700px">
      <el-form :model="editForm" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="8"><el-form-item label="姓名"><el-input v-model="editForm.name" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="性别">
              <el-select v-model="editForm.gender"><el-option label="男" value="男" /><el-option label="女" value="女" /></el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8"><el-form-item label="年龄"><el-input-number v-model="editForm.age" :min="0" :max="120" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8"><el-form-item label="门诊号"><el-input v-model="editForm.patient_no" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="住院号"><el-input v-model="editForm.inpatient_no" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="床号"><el-input v-model="editForm.bed_no" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8"><el-form-item label="科室"><el-input v-model="editForm.department" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="责任医生"><el-input v-model="editForm.responsible_doctor" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="责任护士"><el-input v-model="editForm.responsible_nurse" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="入院日期"><el-date-picker v-model="editForm.admission_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
          </el-col>
          <el-col :span="8"><el-form-item label="西医诊断"><el-input v-model="editForm.diagnosis" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="editForm.status">
                <el-option label="在院" value="在院" /><el-option label="出院" value="出院" />
                <el-option label="随访中" value="随访中" /><el-option label="结案" value="结案" />
                <el-option label="失访" value="失访" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="风险等级">
              <el-select v-model="editForm.risk_level" clearable>
                <el-option label="低风险" value="low" /><el-option label="中风险" value="medium" /><el-option label="高风险" value="high" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8"><el-form-item label="中医诊断"><el-input v-model="editForm.tcm_diagnosis" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="电话"><el-input v-model="editForm.phone" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="过敏史"><el-input v-model="editForm.allergy_history" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="既往史"><el-input v-model="editForm.past_history" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="家族史"><el-input v-model="editForm.family_history" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="入院评估"><el-input v-model="editForm.admission_assessment" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="出院小结"><el-input v-model="editForm.discharge_summary" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="editForm.notes" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>

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
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="deleteTcmScore(row.id)">删除</el-button>
            </template>
          </el-table-column>
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
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="deleteLabTest(row.id)">删除</el-button>
            </template>
          </el-table-column>
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
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="deleteQol(row.id)">删除</el-button>
            </template>
          </el-table-column>
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
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="deleteTreatment(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="疗效评价" name="efficacy">
        <EfficacyView :patientId="patient.id" />
      </el-tab-pane>

      <el-tab-pane label="随访管理" name="followup">
        <FollowupView />
      </el-tab-pane>

      <el-tab-pane label="临床时间轴" name="timeline">
        <ClinicalTimeline :patientId="patient.id" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePatientStore } from '../stores/patient'
import { useClinicalStore } from '../stores/clinical'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import TcmScoreForm from '../components/TcmScoreForm.vue'
import LabTestForm from '../components/LabTestForm.vue'
import QolForm from '../components/QolForm.vue'
import TreatmentForm from '../components/TreatmentForm.vue'
import TrendChart from '../components/TrendChart.vue'
import EfficacyView from '../components/EfficacyView.vue'
import FollowupView from '../views/FollowupView.vue'
import ClinicalTimeline from '../components/ClinicalTimeline.vue'

const route = useRoute()
const store = usePatientStore()
const clinical = useClinicalStore()
const activeTab = ref('tcm')
const showEditDialog = ref(false)
const editForm = ref({})

const patient = computed(() => store.currentPatient)

const tcmChartData = computed(() => ({
  xData: clinical.tcmScores.map(s => s.record_date),
  series: [{ name: '总分', data: clinical.tcmScores.map(s => s.total_score) }],
}))

const labChartData = computed(() => {
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

function openEditDialog() {
  editForm.value = { ...patient.value }
  showEditDialog.value = true
}

async function handleEditSave() {
  await store.updatePatient(route.params.id, editForm.value)
  showEditDialog.value = false
  ElMessage.success('修改成功')
}

async function deleteTcmScore(id) {
  await ElMessageBox.confirm('确认删除此证候评分?', '提示', { type: 'warning' })
  await api.deleteTcmScore(route.params.id, id)
  ElMessage.success('已删除')
  loadTcm()
}

async function deleteLabTest(id) {
  await ElMessageBox.confirm('确认删除此检验记录?', '提示', { type: 'warning' })
  await api.deleteLabTest(route.params.id, id)
  ElMessage.success('已删除')
  loadLab()
}

async function deleteQol(id) {
  await ElMessageBox.confirm('确认删除此生活质量记录?', '提示', { type: 'warning' })
  await api.deleteQol(route.params.id, id)
  ElMessage.success('已删除')
  loadQol()
}

async function deleteTreatment(id) {
  await ElMessageBox.confirm('确认删除此治疗方案?', '提示', { type: 'warning' })
  await api.deleteTreatment(route.params.id, id)
  ElMessage.success('已删除')
  loadTreatment()
}

async function exportPdf() {
  const res = await api.exportPatientPdf(route.params.id)
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = `患者报告_${patient.value?.name || ''}.pdf`
  a.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('PDF已导出')
}

async function exportLabExcel() {
  const res = await api.exportLabExcel(route.params.id)
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = '检验数据.xlsx'
  a.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('Excel已导出')
}

function statusType(status) {
  const map = { '在院': '', '出院': 'success', '随访中': 'warning', '结案': 'info', '失访': 'danger' }
  return map[status] || ''
}
function riskType(level) {
  return level === 'high' ? 'danger' : (level === 'medium' ? 'warning' : 'success')
}
function riskLabel(level) {
  return { low: '低风险', medium: '中风险', high: '高风险' }[level] || level
}

watch(activeTab, (tab) => {
  if (tab === 'tcm') loadTcm()
  if (tab === 'lab') loadLab()
  if (tab === 'qol') loadQol()
  if (tab === 'treatment') loadTreatment()
})
</script>