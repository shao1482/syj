<template>
  <div>
    <el-card>
      <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
        <el-input v-model="search" placeholder="搜索姓名/诊断" style="width: 180px;" clearable size="small" />
        <div>
          <el-button @click="exportExcel">导出Excel</el-button>
          <el-upload :show-file-list="false" :before-upload="importExcel" accept=".xlsx">
            <el-button type="info">导入Excel</el-button>
          </el-upload>
          <el-button type="primary" @click="openAddDialog()">新增患者</el-button>
        </div>
      </div>
      <el-table :data="filteredPatients" stripe @row-click="goDetail" style="cursor: pointer;">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="diagnosis" label="西医诊断" />
        <el-table-column prop="tcm_diagnosis" label="中医诊断" />
        <el-table-column prop="admission_date" label="入院日期" width="120" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click.stop="goDetail(row)">详情</el-button>
            <el-button size="small" type="warning" @click.stop="openEditDialog(row)">修改</el-button>
            <el-button size="small" type="danger" @click.stop="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/修改对话框 -->
    <el-dialog v-model="showDialog" :title="isEdit ? '修改患者' : '新增患者'" width="700px">
      <el-form :model="formData" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名"><el-input v-model="formData.name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="formData.gender">
                <el-option label="男" value="男" /><el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年龄"><el-input-number v-model="formData.age" :min="0" :max="120" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话"><el-input v-model="formData.phone" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入院日期"><el-date-picker v-model="formData.admission_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="西医诊断"><el-input v-model="formData.diagnosis" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="中医诊断"><el-input v-model="formData.tcm_diagnosis" /></el-form-item>
        <el-form-item label="过敏史"><el-input v-model="formData.allergy_history" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="既往史"><el-input v-model="formData.past_history" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="家族史"><el-input v-model="formData.family_history" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="入院评估"><el-input v-model="formData.admission_assessment" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="出院小结"><el-input v-model="formData.discharge_summary" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="formData.notes" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ isEdit ? '保存修改' : '确认新增' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePatientStore } from '../stores/patient'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const store = usePatientStore()
const search = ref('')
const showDialog = ref(false)
const isEdit = ref(false)
const editId = ref(null)

const emptyForm = () => ({
  name: '', gender: '男', age: 50, phone: '', admission_date: '',
  diagnosis: '', tcm_diagnosis: '', notes: '',
  allergy_history: '', past_history: '', family_history: '',
  admission_assessment: '', discharge_summary: '',
})
const formData = ref(emptyForm())

const filteredPatients = computed(() => {
  if (!search.value) return store.patients
  const s = search.value.toLowerCase()
  return store.patients.filter(p =>
    p.name.toLowerCase().includes(s) || (p.diagnosis && p.diagnosis.toLowerCase().includes(s))
  )
})

onMounted(() => store.fetchPatients())

function goDetail(row) { router.push(`/patients/${row.id}`) }

function openAddDialog() {
  isEdit.value = false
  editId.value = null
  formData.value = emptyForm()
  showDialog.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editId.value = row.id
  formData.value = { ...row }
  showDialog.value = true
}

async function handleSubmit() {
  if (isEdit.value) {
    await store.updatePatient(editId.value, formData.value)
    ElMessage.success('修改成功')
  } else {
    await store.createPatient(formData.value)
    ElMessage.success('新增成功')
  }
  showDialog.value = false
  formData.value = emptyForm()
}

async function handleDelete(id) {
  await store.deletePatient(id)
  ElMessage.success('已删除')
}

async function exportExcel() {
  const res = await api.exportPatientsExcel()
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = '患者列表.xlsx'
  a.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

async function importExcel(file) {
  const res = await api.importPatientsExcel(file)
  ElMessage.success(res.data.message)
  store.fetchPatients()
  return false
}
</script>