import { defineStore } from 'pinia'
import api from '../api'

export const usePatientStore = defineStore('patient', {
  state: () => ({
    patients: [],
    currentPatient: null,
  }),
  actions: {
    async fetchPatients() {
      const res = await api.getPatients()
      this.patients = res.data
    },
    async fetchPatient(id) {
      const res = await api.getPatient(id)
      this.currentPatient = res.data
    },
    async createPatient(data) {
      const res = await api.createPatient(data)
      this.patients.push(res.data)
      return res.data
    },
    async updatePatient(id, data) {
      const res = await api.updatePatient(id, data)
      const idx = this.patients.findIndex(p => p.id === id)
      if (idx >= 0) this.patients[idx] = res.data
      return res.data
    },
    async deletePatient(id) {
      await api.deletePatient(id)
      this.patients = this.patients.filter(p => p.id !== id)
    },
  },
})