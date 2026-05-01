<template>
  <el-card header="录入实验室检验" style="margin-bottom: 16px;">
    <el-form :model="form" label-width="100px" inline>
      <el-form-item label="日期"><el-date-picker v-model="form.record_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
      <el-form-item label="类型">
        <el-select v-model="form.test_type" style="width: 120px;">
          <el-option label="血常规" value="blood_routine" />
          <el-option label="肝功能" value="liver_func" />
          <el-option label="胃功能" value="gastric" />
        </el-select>
      </el-form-item>
      <el-form-item label="WBC">
        <el-input-number v-model="form.wbc" :precision="1" size="small" />
        <el-tag v-if="isAbnormal('wbc', form.wbc)" type="danger" size="small" style="margin-left:4px;">异常</el-tag>
      </el-form-item>
      <el-form-item label="RBC"><el-input-number v-model="form.rbc" :precision="1" size="small" /></el-form-item>
      <el-form-item label="HGB">
        <el-input-number v-model="form.hgb" :precision="1" size="small" />
        <el-tag v-if="isAbnormal('hgb', form.hgb)" type="danger" size="small" style="margin-left:4px;">异常</el-tag>
      </el-form-item>
      <el-form-item label="PLT"><el-input-number v-model="form.plt" :precision="1" size="small" /></el-form-item>
      <el-form-item label="ALT">
        <el-input-number v-model="form.alt" :precision="1" size="small" />
        <el-tag v-if="isAbnormal('alt', form.alt)" type="danger" size="small" style="margin-left:4px;">偏高</el-tag>
      </el-form-item>
      <el-form-item label="AST">
        <el-input-number v-model="form.ast" :precision="1" size="small" />
        <el-tag v-if="isAbnormal('ast', form.ast)" type="danger" size="small" style="margin-left:4px;">偏高</el-tag>
      </el-form-item>
      <el-form-item label="TBIL">
        <el-input-number v-model="form.tbil" :precision="1" size="small" />
        <el-tag v-if="isAbnormal('tbil', form.tbil)" type="danger" size="small" style="margin-left:4px;">偏高</el-tag>
      </el-form-item>
      <el-form-item label="ALB">
        <el-input-number v-model="form.alb" :precision="1" size="small" />
        <el-tag v-if="isAbnormal('alb', form.alb)" type="danger" size="small" style="margin-left:4px;">偏低</el-tag>
      </el-form-item>
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

const THRESHOLDS = {
  wbc: { low: 3.5, high: 9.5 },
  rbc: { low: 3.5, high: 5.5 },
  hgb: { low: 90, high: 160 },
  plt: { low: 100, high: 300 },
  alt: { high: 40 },
  ast: { high: 40 },
  tbil: { high: 17.1 },
  alb: { low: 35 },
}

const form = ref({
  record_date: '', test_type: 'blood_routine',
  wbc: null, rbc: null, hgb: null, plt: null,
  alt: null, ast: null, tbil: null, alb: null,
  gastrin: null, pepsinogen_i: null, pepsinogen_ii: null,
  other_name: null, other_value: null,
})

function isAbnormal(field, value) {
  if (value === null || value === undefined) return false
  const t = THRESHOLDS[field]
  if (!t) return false
  if (t.high && value > t.high) return true
  if (t.low && value < t.low) return true
  return false
}

async function submit() {
  if (!form.value.record_date) {
    ElMessage.warning('请选择日期')
    return
  }
  try {
    await api.createLabTest(props.patientId, form.value)
    ElMessage.success('提交成功（已自动触发预警检查）')
    emit('saved')
  } catch (e) {
    ElMessage.error('提交失败: ' + (e.response?.data?.detail || e.message))
  }
}
</script>