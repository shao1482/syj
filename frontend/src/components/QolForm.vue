<template>
  <el-card header="录入生活质量评估" style="margin-bottom: 16px;">
    <el-form :model="form" label-width="100px" inline>
      <el-form-item label="日期"><el-date-picker v-model="form.record_date" type="date" /></el-form-item>
      <el-form-item label="营养评分"><el-input-number v-model="form.nutrition_score" :min="0" :max="10" size="small" /></el-form-item>
      <el-form-item label="疼痛评分"><el-input-number v-model="form.pain_score" :min="0" :max="10" size="small" /></el-form-item>
      <el-form-item label="睡眠评分"><el-input-number v-model="form.sleep_score" :min="0" :max="10" size="small" /></el-form-item>
      <el-form-item label="生理功能"><el-input-number v-model="form.physical_function" :min="0" :max="10" size="small" /></el-form-item>
      <el-form-item label="心理健康"><el-input-number v-model="form.mental_health" :min="0" :max="10" size="small" /></el-form-item>
      <el-form-item label="社会功能"><el-input-number v-model="form.social_function" :min="0" :max="10" size="small" /></el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submit">提交</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const props = defineProps({ patientId: Number })
const emit = defineEmits(['saved'])

const form = ref({
  record_date: '', nutrition_score: 0, pain_score: 0, sleep_score: 0,
  physical_function: 0, mental_health: 0, social_function: 0, total_score: 0,
})

async function submit() {
  form.value.total_score = form.value.nutrition_score + form.value.pain_score +
    form.value.sleep_score + form.value.physical_function +
    form.value.mental_health + form.value.social_function
  await api.createQol(props.patientId, form.value)
  emit('saved')
}
</script>