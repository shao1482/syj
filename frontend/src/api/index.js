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
  updateTcmScore: (pid, id, data) => request.put(`/patients/${pid}/tcm-scores/${id}`, data),
  deleteTcmScore: (pid, id) => request.delete(`/patients/${pid}/tcm-scores/${id}`),

  // 实验室检验
  getLabTests: (pid) => request.get(`/patients/${pid}/lab-tests/`),
  createLabTest: (pid, data) => request.post(`/patients/${pid}/lab-tests/`, data),
  updateLabTest: (pid, id, data) => request.put(`/patients/${pid}/lab-tests/${id}`, data),
  deleteLabTest: (pid, id) => request.delete(`/patients/${pid}/lab-tests/${id}`),

  // 生活质量
  getQol: (pid) => request.get(`/patients/${pid}/qol/`),
  createQol: (pid, data) => request.post(`/patients/${pid}/qol/`, data),
  updateQol: (pid, id, data) => request.put(`/patients/${pid}/qol/${id}`, data),
  deleteQol: (pid, id) => request.delete(`/patients/${pid}/qol/${id}`),

  // 治疗方案
  getTreatments: (pid) => request.get(`/patients/${pid}/treatments/`),
  createTreatment: (pid, data) => request.post(`/patients/${pid}/treatments/`, data),
  updateTreatment: (pid, id, data) => request.put(`/patients/${pid}/treatments/${id}`, data),
  deleteTreatment: (pid, id) => request.delete(`/patients/${pid}/treatments/${id}`),

  // 预警
  getAlerts: (params) => request.get('/alerts/list', { params }),
  resolveAlert: (id) => request.put(`/alerts/${id}`, { status: 'resolved' }),
  getAlertConfig: () => request.get('/alerts/config'),
  updateAlertConfig: (data) => request.put('/alerts/config', data),

  // AI数据分析
  aiAnalysis: (pid) => request.post(`/reports/ai-analysis/${pid}`),
  agentAnalysis: (pid) => request.post(`/reports/agent-analysis/${pid}`),
  getAnalysisConfig: () => request.get('/reports/analysis-config'),
  updateAnalysisConfig: (data) => request.put('/reports/analysis-config', data),

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
  updateFollowup: (pid, id, data) => request.put(`/patients/${pid}/followups/${id}`, data),
  deleteFollowup: (pid, id) => request.delete(`/patients/${pid}/followups/${id}`),
  getFollowupReminders: () => request.get('/followups/reminders/'),

  // 临床时间轴
  getTimeline: (pid) => request.get(`/patients/${pid}/timeline/`),
}