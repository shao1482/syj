import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export default {
  // 患者
  getPatients: () => request.get('/patients/'),
  createPatient: (data) => request.post('/patients/', data),
  getPatient: (id) => request.get(`/patients/${id}`),
  updatePatient: (id, data) => request.put(`/patients/${id}`, data),
  deletePatient: (id) => request.delete(`/patients/${id}`),

  // 中医证候
  getTcmScores: (pid) => request.get(`/patients/${pid}/tcm-scores/`),
  createTcmScore: (pid, data) => request.post(`/patients/${pid}/tcm-scores/`, data),

  // 实验室检验
  getLabTests: (pid) => request.get(`/patients/${pid}/lab-tests/`),
  createLabTest: (pid, data) => request.post(`/patients/${pid}/lab-tests/`, data),

  // 生活质量
  getQol: (pid) => request.get(`/patients/${pid}/qol/`),
  createQol: (pid, data) => request.post(`/patients/${pid}/qol/`, data),

  // 治疗方案
  getTreatments: (pid) => request.get(`/patients/${pid}/treatments/`),
  createTreatment: (pid, data) => request.post(`/patients/${pid}/treatments/`, data),

  // 预警
  getAlerts: (params) => request.get('/alerts/list', { params }),
  resolveAlert: (id) => request.put(`/alerts/${id}`, { status: 'resolved' }),
  getAlertConfig: () => request.get('/alerts/config'),
  updateAlertConfig: (data) => request.put('/alerts/config', data),

  // AI数据分析
  aiAnalysis: (pid) => request.post(`/reports/ai-analysis/${pid}`),

  // 报表
  getOverview: () => request.get('/reports/overview'),
  getTrend: (pid) => request.get(`/reports/trend/${pid}`),

  // PDF导出
  exportPatientPdf: (id) => request.get(`/reports/patient/${id}/pdf`, { responseType: 'blob' }),

  // Excel导入导出
  exportPatientsExcel: () => request.get('/reports/export/patients', { responseType: 'blob' }),
  exportLabExcel: (pid) => request.get(`/reports/export/lab-tests/${pid}`, { responseType: 'blob' }),
  importPatientsExcel: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/reports/import/patients', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  },

  // 疗效评价
  getEfficacy: (pid) => request.get(`/reports/efficacy/${pid}`),

  // 随访管理
  getFollowups: (pid) => request.get(`/patients/${pid}/followups/`),
  createFollowup: (pid, data) => request.post(`/patients/${pid}/followups/`, data),
  getFollowupReminders: () => request.get('/followups/reminders/'),
}