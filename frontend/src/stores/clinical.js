import { defineStore } from 'pinia'
import api from '../api'

export const useClinicalStore = defineStore('clinical', {
  state: () => ({
    tcmScores: [],
    labTests: [],
    qolRecords: [],
    treatments: [],
  }),
  actions: {
    async fetchTcmScores(pid) {
      this.tcmScores = (await api.getTcmScores(pid)).data
    },
    async createTcmScore(pid, data) {
      const res = await api.createTcmScore(pid, data)
      this.tcmScores.push(res.data)
    },
    async fetchLabTests(pid) {
      this.labTests = (await api.getLabTests(pid)).data
    },
    async createLabTest(pid, data) {
      const res = await api.createLabTest(pid, data)
      this.labTests.push(res.data)
    },
    async fetchQol(pid) {
      this.qolRecords = (await api.getQol(pid)).data
    },
    async createQol(pid, data) {
      const res = await api.createQol(pid, data)
      this.qolRecords.push(res.data)
    },
    async fetchTreatments(pid) {
      this.treatments = (await api.getTreatments(pid)).data
    },
    async createTreatment(pid, data) {
      const res = await api.createTreatment(pid, data)
      this.treatments.push(res.data)
    },
  },
})