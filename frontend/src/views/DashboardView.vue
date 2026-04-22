<template>
  <div class="dashboard-grid">
    <PriceCard />

    <div class="card chart-section">
      <div class="chart-tabs">
        <button :class="{ active: chartType === 'kline' }" @click="chartType = 'kline'">K线</button>
        <button :class="{ active: chartType === 'trend' }" @click="chartType = 'trend'">趋势</button>
      </div>
      <div class="chart-controls">
        <button
          v-for="item in intervals"
          :key="item.value"
          :class="{ active: selectedInterval === item.value }"
          @click="changeInterval(item.value)"
        >
          {{ item.label }}
        </button>
      </div>
      <div v-if="loading" class="loading">加载中...</div>
      <KLineChart v-else-if="chartType === 'kline'" :data="klineData" :interval="selectedInterval" />
      <TrendLineChart v-else :data="klineData" :interval="selectedInterval" />
    </div>

    <ForecastCard :forecast="forecast" :loading="forecastLoading" />

    <QuantAnalysis :quant="quant" :loading="quantLoading" />

    <GeopoliticalCard />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePriceStore } from '../stores/price'
import PriceCard from '../components/PriceCard.vue'
import KLineChart from '../components/KLineChart.vue'
import TrendLineChart from '../components/TrendLineChart.vue'
import ForecastCard from '../components/ForecastCard.vue'
import QuantAnalysis from '../components/QuantAnalysis.vue'
import GeopoliticalCard from '../components/GeopoliticalCard.vue'

const priceStore = usePriceStore()
const chartType = ref('kline')
const intervals = [
  { value: '5m', label: '5分钟' },
  { value: '15m', label: '15分钟' },
  { value: '1h', label: '1小时' },
  { value: '4h', label: '4小时' },
  { value: '1d', label: '1天' },
]
const selectedInterval = computed(() => priceStore.selectedInterval)
const klineData = computed(() => priceStore.klineData)
const loading = computed(() => priceStore.loading)
const forecast = computed(() => priceStore.forecast)
const forecastLoading = ref(false)
const quant = computed(() => priceStore.quant)
const quantLoading = ref(false)

function changeInterval(interval) {
  priceStore.setInterval(interval)
}

onMounted(async () => {
  await Promise.all([
    priceStore.fetchCurrentPrice(),
    priceStore.fetchKline(),
  ])
  forecastLoading.value = true
  quantLoading.value = true
  await Promise.all([
    priceStore.fetchForecast(),
    priceStore.fetchQuant(),
  ])
  forecastLoading.value = false
  quantLoading.value = false
})
</script>
