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
  getAlerts: (params) => request.get('/alerts/', { params }),
  resolveAlert: (id) => request.put(`/alerts/${id}`, { status: 'resolved' }),

  // 报表
  getOverview: () => request.get('/reports/overview'),
  getTrend: (pid) => request.get(`/reports/trend/${pid}`),
}