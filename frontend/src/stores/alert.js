import { defineStore } from 'pinia'
import { ref } from 'vue'
import { alertApi } from '../api'

export const useAlertStore = defineStore('alert', () => {
  const alerts = ref([])
  const triggeredAlerts = ref([])
  const loading = ref(false)

  async function fetchAlerts() {
    loading.value = true
    try {
      const { data } = await alertApi.list()
      alerts.value = data
    } catch (e) {
      console.error('Failed to fetch alerts:', e)
    } finally {
      loading.value = false
    }
  }

  async function createAlert(alertData) {
    try {
      const { data } = await alertApi.create(alertData)
      alerts.value.unshift(data)
      return data
    } catch (e) {
      console.error('Failed to create alert:', e)
      throw e
    }
  }

  async function updateAlert(id, alertData) {
    try {
      const { data } = await alertApi.update(id, alertData)
      const idx = alerts.value.findIndex(a => a.id === id)
      if (idx !== -1) alerts.value[idx] = data
      return data
    } catch (e) {
      console.error('Failed to update alert:', e)
      throw e
    }
  }

  async function deleteAlert(id) {
    try {
      await alertApi.delete(id)
      alerts.value = alerts.value.filter(a => a.id !== id)
    } catch (e) {
      console.error('Failed to delete alert:', e)
      throw e
    }
  }

  function addTriggeredAlert(alert) {
    triggeredAlerts.value.unshift(alert)
    if (triggeredAlerts.value.length > 20) {
      triggeredAlerts.value.pop()
    }
  }

  function dismissTriggered(index) {
    triggeredAlerts.value.splice(index, 1)
  }

  return {
    alerts, triggeredAlerts, loading,
    fetchAlerts, createAlert, updateAlert, deleteAlert,
    addTriggeredAlert, dismissTriggered,
  }
})
