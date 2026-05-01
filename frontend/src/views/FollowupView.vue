<template>
  <div>
    <el-card header="随访管理">
      <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
        <span>随访计划列表</span>
        <el-button type="primary" @click="showAddDialog = true">新增随访计划</el-button>
      </div>

      <el-table :data="followups" stripe>
        <el-table-column prop="plan_date" label="计划日期" width="120" />
        <el-table-column prop="actual_date" label="实际日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="随访内容" />
        <el-table-column prop="symptom_change" label="症状变化" />
        <el-table-column prop="doctor_advice" label="医嘱" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="handleComplete(row.id)" v-if="row.status !== 'completed'">完成</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新增随访计划" width="500px">
      <el-form :model="newFollowup" label-width="80px">
        <el-form-item label="计划日期"><el-date-picker v-model="newFollowup.plan_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="随访内容"><el-input v-model="newFollowup.content" type="textarea" /></el-form-item>
        <el-form-item label="症状变化"><el-input v-model="newFollowup.symptom_change" type="textarea" /></el-form-item>
        <el-form-item label="医嘱"><el-input v-model="newFollowup.doctor_advice" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const followups = ref([])
const showAddDialog = ref(false)
const newFollowup = ref({ plan_date: '', content: '', symptom_change: '', doctor_advice: '' })

async function loadFollowups() {
  const res = await api.getFollowups(route.params.id)
  followups.value = res.data
}

onMounted(() => loadFollowups())
watch(() => route.params.id, () => loadFollowups())

async function handleAdd() {
  await api.createFollowup(route.params.id, newFollowup.value)
  showAddDialog.value = false
  ElMessage.success('随访计划已添加')
  loadFollowups()
  newFollowup.value = { plan_date: '', content: '', symptom_change: '', doctor_advice: '' }
}

async function handleComplete(id) {
  const item = followups.value.find(f => f.id === id)
  await api.createFollowup(route.params.id, { ...item, status: 'completed', actual_date: new Date().toISOString().slice(0, 10) })
  ElMessage.success('随访已完成')
  loadFollowups()
}

function statusType(status) {
  if (status === 'completed') return 'success'
  if (status === 'overdue') return 'danger'
  return 'warning'
}
function statusLabel(status) {
  const map = { planned: '计划中', completed: '已完成', overdue: '已逾期' }
  return map[status] || status
}
</script>