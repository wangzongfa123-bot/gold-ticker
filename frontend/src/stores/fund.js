import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fundApi } from '../api'

export const useFundStore = defineStore('fund', () => {
  const funds = ref([])
  const loading = ref(false)
  const navCache = ref({})
  const analysisCache = ref({})

  async function fetchFunds(category) {
    loading.value = true
    try {
      const { data } = await fundApi.list(category || undefined)
      funds.value = data
    } catch (e) {
      console.error('Failed to fetch funds:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchNav(code) {
    if (navCache.value[code]) return navCache.value[code]
    try {
      const { data } = await fundApi.getNav(code, 30)
      navCache.value[code] = data
      return data
    } catch (e) {
      console.error('Failed to fetch NAV for', code, e)
      return null
    }
  }

  async function fetchAnalysis(code) {
    if (analysisCache.value[code]) return analysisCache.value[code]
    try {
      const { data } = await fundApi.getAnalysis(code)
      analysisCache.value[code] = data
      return data
    } catch (e) {
      console.error('Failed to fetch analysis for', code, e)
      return null
    }
  }

  function clearCache(code) {
    delete navCache.value[code]
    delete analysisCache.value[code]
  }

  return {
    funds, loading, navCache, analysisCache,
    fetchFunds, fetchNav, fetchAnalysis, clearCache,
  }
})
