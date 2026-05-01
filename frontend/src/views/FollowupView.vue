<template>
  <div>
    <el-card header="随访管理">
      <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
        <span>随访计划列表</span>
        <el-button type="primary" size="small" @click="openAddDialog">新增随访计划</el-button>
      </div>

      <el-table :data="followups" stripe>
        <el-table-column prop="plan_date" label="计划日期" width="120" />
        <el-table-column prop="actual_date" label="实际日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="随访内容" />
        <el-table-column prop="symptom_change" label="症状变化" />
        <el-table-column prop="doctor_advice" label="医嘱" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="handleComplete(row)" v-if="row.status === 'planned'">完成</el-button>
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增随访对话框 -->
    <el-dialog v-model="showAddDialog" title="新增随访计划" width="500px">
      <el-form :model="newFollowup" label-width="80px" :rules="rules" ref="addFormRef">
        <el-form-item label="计划日期" prop="plan_date">
          <el-date-picker v-model="newFollowup.plan_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="随访内容"><el-input v-model="newFollowup.content" type="textarea" /></el-form-item>
        <el-form-item label="症状变化"><el-input v-model="newFollowup.symptom_change" type="textarea" /></el-form-item>
        <el-form-item label="医嘱"><el-input v-model="newFollowup.doctor_advice" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确认</el-button>
      </template>
    </el-dialog>

    <!-- 编辑随访对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑随访计划" width="500px">
      <el-form :model="editFollowup" label-width="80px">
        <el-form-item label="计划日期">
          <el-date-picker v-model="editFollowup.plan_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="实际日期">
          <el-date-picker v-model="editFollowup.actual_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editFollowup.status">
            <el-option label="计划中" value="planned" />
            <el-option label="已完成" value="completed" />
            <el-option label="已逾期" value="overdue" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="随访内容"><el-input v-model="editFollowup.content" type="textarea" /></el-form-item>
        <el-form-item label="症状变化"><el-input v-model="editFollowup.symptom_change" type="textarea" /></el-form-item>
        <el-form-item label="医嘱"><el-input v-model="editFollowup.doctor_advice" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const followups = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addFormRef = ref(null)
const newFollowup = ref({ plan_date: '', content: '', symptom_change: '', doctor_advice: '' })
const editFollowup = ref({})
const editId = ref(null)

const rules = { plan_date: [{ required: true, message: '请选择计划日期', trigger: 'change' }] }

async function loadFollowups() {
  const res = await api.getFollowups(route.params.id)
  followups.value = res.data
}

onMounted(() => loadFollowups())
watch(() => route.params.id, () => loadFollowups())

function openAddDialog() {
  newFollowup.value = { plan_date: '', content: '', symptom_change: '', doctor_advice: '' }
  showAddDialog.value = true
}

async function handleAdd() {
  if (!newFollowup.value.plan_date) {
    ElMessage.warning('请选择计划日期')
    return
  }
  await api.createFollowup(route.params.id, newFollowup.value)
  showAddDialog.value = false
  ElMessage.success('随访计划已添加')
  loadFollowups()
}

function openEditDialog(row) {
  editFollowup.value = { ...row }
  editId.value = row.id
  showEditDialog.value = true
}

async function handleEditSave() {
  await api.updateFollowup(route.params.id, editId.value, editFollowup.value)
  showEditDialog.value = false
  ElMessage.success('已保存')
  loadFollowups()
}

async function handleComplete(row) {
  await api.updateFollowup(route.params.id, row.id, {
    ...row, status: 'completed', actual_date: new Date().toISOString().slice(0, 10),
  })
  ElMessage.success('随访已完成')
  loadFollowups()
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确认删除此随访计划?', '提示', { type: 'warning' })
  await api.deleteFollowup(route.params.id, id)
  ElMessage.success('已删除')
  loadFollowups()
}

function statusType(status) {
  if (status === 'completed') return 'success'
  if (status === 'overdue') return 'danger'
  if (status === 'cancelled') return 'info'
  return 'warning'
}
function statusLabel(status) {
  const map = { planned: '计划中', completed: '已完成', overdue: '已逾期', cancelled: '已取消' }
  return map[status] || status
}
</script>