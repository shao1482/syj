import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/patients' },
  { path: '/patients', component: () => import('../views/PatientList.vue') },
  { path: '/patients/:id', component: () => import('../views/PatientDetail.vue') },
  { path: '/dashboard', component: () => import('../views/ClinicalDashboard.vue') },
  { path: '/alerts', component: () => import('../views/AlertCenter.vue') },
  { path: '/reports', component: () => import('../views/ReportView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})