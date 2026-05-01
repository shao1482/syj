<template>
  <div>
    <el-card>
      <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
        <el-input v-model="search" placeholder="搜索患者姓名/诊断" style="width: 300px;" clearable />
        <el-button type="primary" @click="showAddDialog = true">新增患者</el-button>
      </div>
      <el-table :data="filteredPatients" stripe @row-click="goDetail" style="cursor: pointer;">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="diagnosis" label="西医诊断" />
        <el-table-column prop="tcm_diagnosis" label="中医诊断" />
        <el-table-column prop="admission_date" label="入院日期" width="120" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click.stop="goDetail(row)">详情</el-button>
            <el-button size="small" type="danger" @click.stop="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新增患者" width="500px">
      <el-form :model="newPatient" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="newPatient.name" /></el-form-item>
        <el-form-item label="性别">
          <el-select v-model="newPatient.gender">
            <el-option label="男" value="男" /><el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄"><el-input-number v-model="newPatient.age" :min="0" :max="120" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="newPatient.phone" /></el-form-item>
        <el-form-item label="入院日期"><el-date-picker v-model="newPatient.admission_date" type="date" /></el-form-item>
        <el-form-item label="西医诊断"><el-input v-model="newPatient.diagnosis" /></el-form-item>
        <el-form-item label="中医诊断"><el-input v-model="newPatient.tcm_diagnosis" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="newPatient.notes" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePatientStore } from '../stores/patient'

const router = useRouter()
const store = usePatientStore()
const search = ref('')
const showAddDialog = ref(false)
const newPatient = ref({ name: '', gender: '男', age: 50, phone: '', admission_date: '', diagnosis: '', tcm_diagnosis: '', notes: '' })

const filteredPatients = computed(() => {
  if (!search.value) return store.patients
  const s = search.value.toLowerCase()
  return store.patients.filter(p =>
    p.name.toLowerCase().includes(s) || (p.diagnosis && p.diagnosis.toLowerCase().includes(s))
  )
})

onMounted(() => store.fetchPatients())

function goDetail(row) {
  router.push(`/patients/${row.id}`)
}

async function handleAdd() {
  await store.createPatient(newPatient.value)
  showAddDialog.value = false
  newPatient.value = { name: '', gender: '男', age: 50, phone: '', admission_date: '', diagnosis: '', tcm_diagnosis: '', notes: '' }
}

async function handleDelete(id) {
  await store.deletePatient(id)
}
</script>