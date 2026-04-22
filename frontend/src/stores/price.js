import { defineStore } from 'pinia'
import { ref } from 'vue'
import { priceApi } from '../api'

export const usePriceStore = defineStore('price', () => {
  const currentPrice = ref({
    price_cny: 0,
    change: null,
    change_percent: null,
    high_24h: null,
    low_24h: null,
    timestamp: null,
  })
  const klineData = ref([])
  const priceHistory = ref([])
  const selectedInterval = ref('1h')
  const isConnected = ref(false)
  const loading = ref(false)
  const forecast = ref({})
  const quant = ref({})

  async function fetchCurrentPrice() {
    try {
      const { data } = await priceApi.getCurrent()
      currentPrice.value = data
    } catch (e) {
      console.error('Failed to fetch current price:', e)
    }
  }

  async function fetchKline(interval, limit = 100) {
    loading.value = true
    try {
      const { data } = await priceApi.getKline({ interval: interval || selectedInterval.value, limit })
      klineData.value = data
    } catch (e) {
      console.error('Failed to fetch kline:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(params) {
    loading.value = true
    try {
      const { data } = await priceApi.getHistory(params)
      priceHistory.value = data
    } catch (e) {
      console.error('Failed to fetch history:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchForecast(hours = 48) {
    try {
      const { data } = await priceApi.getForecast({ hours })
      forecast.value = data
    } catch (e) {
      console.error('Failed to fetch forecast:', e)
    }
  }

  async function fetchQuant() {
    try {
      const { data } = await priceApi.getQuant()
      quant.value = data
    } catch (e) {
      console.error('Failed to fetch quant analysis:', e)
    }
  }

  function updatePrice(data) {
    currentPrice.value = { ...currentPrice.value, ...data }
  }

  function setInterval(interval) {
    selectedInterval.value = interval
    fetchKline(interval)
  }

  return {
    currentPrice, klineData, priceHistory, selectedInterval,
    isConnected, loading, forecast, quant,
    fetchCurrentPrice, fetchKline, fetchHistory, updatePrice, setInterval,
    fetchForecast, fetchQuant,
  }
})
