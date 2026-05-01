<template>
  <el-card header="录入中医证候评分" style="margin-bottom: 16px;">
    <el-form :model="form" label-width="100px" inline>
      <el-form-item label="日期"><el-date-picker v-model="form.record_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item label="脾胃虚弱"><el-input-number v-model="form.spleen_stomach_weak" :min="0" :max="30" size="small" /></el-form-item>
      <el-form-item label="肝胃不和"><el-input-number v-model="form.liver_stomachdisharmony" :min="0" :max="30" size="small" /></el-form-item>
      <el-form-item label="脾胃湿热"><el-input-number v-model="form.spleen_stomach_dampheat" :min="0" :max="30" size="small" /></el-form-item>
      <el-form-item label="胃阴不足"><el-input-number v-model="form.stomach_yin_deficiency" :min="0" :max="30" size="small" /></el-form-item>
      <el-form-item label="舌象评分"><el-input-number v-model="form.tongue_score" :min="0" :max="15" size="small" /></el-form-item>
      <el-form-item label="脉象评分"><el-input-number v-model="form.pulse_score" :min="0" :max="15" size="small" /></el-form-item>
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
  record_date: '', spleen_stomach_weak: 0, liver_stomachdisharmony: 0,
  spleen_stomach_dampheat: 0, stomach_yin_deficiency: 0,
  tongue_score: 0, pulse_score: 0, total_score: 0,
})

async function submit() {
  if (!form.value.record_date) {
    ElMessage.warning('请选择日期')
    return
  }
  try {
    form.value.total_score = form.value.spleen_stomach_weak + form.value.liver_stomachdisharmony +
      form.value.spleen_stomach_dampheat + form.value.stomach_yin_deficiency +
      form.value.tongue_score + form.value.pulse_score
    await api.createTcmScore(props.patientId, form.value)
    ElMessage.success('提交成功')
    emit('saved')
    form.value = { record_date: '', spleen_stomach_weak: 0, liver_stomachdisharmony: 0,
      spleen_stomach_dampheat: 0, stomach_yin_deficiency: 0, tongue_score: 0, pulse_score: 0, total_score: 0 }
  } catch (e) {
    ElMessage.error('提交失败: ' + (e.response?.data?.detail || e.message))
  }
}
</script>