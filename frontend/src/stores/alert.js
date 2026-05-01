import { defineStore } from 'pinia'
import api from '../api'

export const useAlertStore = defineStore('alert', {
  state: () => ({
    alerts: [],
  }),
  actions: {
    async fetchAlerts(params = {}) {
      this.alerts = (await api.getAlerts(params)).data
    },
    async resolveAlert(id) {
      await api.resolveAlert(id)
      this.alerts = this.alerts.map(a => a.id === id ? { ...a, status: 'resolved' } : a)
    },
  },
  getters: {
    pendingCount: (state) => state.alerts.filter(a => a.status === 'pending').length,
  },
})