<template>
  <el-card header="录入治疗方案" style="margin-bottom: 16px;">
    <el-form :model="form" label-width="100px">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="方剂名称"><el-input v-model="form.formula_name" /></el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="西药名称"><el-input v-model="form.western_medicine" /></el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="剂量"><el-input v-model="form.dosage" /></el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="方剂组成"><el-input v-model="form.formula_composition" type="textarea" /></el-form-item>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="疗效评价">
            <el-rate v-model="form.effect_rating" :max="5" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="随访记录"><el-input v-model="form.followup_note" type="textarea" /></el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submit">提交</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps({ patientId: Number })
const emit = defineEmits(['saved'])

const form = ref({
  start_date: '', end_date: null,
  formula_name: '', formula_composition: '',
  western_medicine: '', dosage: '',
  effect_rating: 3, followup_note: '',
})

async function submit() {
  if (!form.value.start_date) {
    ElMessage.warning('请选择开始日期')
    return
  }
  try {
    await api.createTreatment(props.patientId, form.value)
    ElMessage.success('提交成功')
    emit('saved')
    form.value = { start_date: '', end_date: null, formula_name: '', formula_composition: '',
      western_medicine: '', dosage: '', effect_rating: 3, followup_note: '' }
  } catch (e) {
    ElMessage.error('提交失败: ' + (e.response?.data?.detail || e.message))
  }
}
</script>