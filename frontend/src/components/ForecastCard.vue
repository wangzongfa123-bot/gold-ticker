<template>
  <div class="card forecast-card">
    <div class="section-header">
      <h3>趋势预测</h3>
      <span class="confidence-badge" :class="forecast.confidence || ''">
        置信度: {{ confidenceLabel }}
      </span>
    </div>

    <div v-if="loading" class="loading">分析中...</div>
    <template v-else-if="forecast.forecast?.length">
      <div class="forecast-summary">
        <div class="trend-badge" :class="trendClass">
          {{ trendLabel }}
          <span class="trend-strength">{{ forecast.trend_strength }}%</span>
        </div>
        <div class="forecast-stats">
          <div class="stat">
            <span class="stat-label">当前价</span>
            <span class="stat-value">¥{{ formatPrice(forecast.current_price) }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">短期均线</span>
            <span class="stat-value">¥{{ formatPrice(forecast.mom_short_avg) }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">长期均线</span>
            <span class="stat-value">¥{{ formatPrice(forecast.mom_long_avg) }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">预测区间</span>
            <span class="stat-value">¥{{ formatPrice(predictedLow) }} - ¥{{ formatPrice(predictedHigh) }}</span>
          </div>
        </div>
      </div>

      <div ref="chartRef" class="forecast-chart"></div>
    </template>
    <div v-else class="empty-state">暂无预测数据，请先获取K线数据</div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  forecast: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
})

const chartRef = ref(null)
let chart = null

const confidenceLabel = computed(() => {
  const map = { high: '高', medium: '中', low: '低' }
  return map[props.forecast.confidence] || '--'
})

const trendLabel = computed(() => {
  const map = { up: '看涨', down: '看跌', flat: '震荡' }
  return map[props.forecast.trend] || '--'
})

const trendClass = computed(() => {
  const map = { up: 'up', down: 'down', flat: 'flat' }
  return map[props.forecast.trend] || 'flat'
})

const predictedLow = computed(() => {
  if (!props.forecast.forecast?.length) return 0
  return Math.min(...props.forecast.forecast.map(f => f.lower))
})

const predictedHigh = computed(() => {
  if (!props.forecast.forecast?.length) return 0
  return Math.max(...props.forecast.forecast.map(f => f.upper))
})

function formatPrice(val) {
  if (val == null) return '--'
  return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatTime(ts) {
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function buildOption() {
  const data = props.forecast.forecast || []
  const times = data.map(d => formatTime(d.timestamp))
  const predicted = data.map(d => d.predicted)
  const upper = data.map(d => d.upper)
  const lower = data.map(d => d.lower)

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a1d28',
      borderColor: '#2a2d3a',
      textStyle: { color: '#e4e6eb' },
      formatter: (params) => {
        if (!params.length) return ''
        const idx = params[0].dataIndex
        return `${params[0].axisValue}<br/>
          预测价: <b>¥${predicted[idx]}</b><br/>
          上轨: ¥${upper[idx]}<br/>
          下轨: ¥${lower[idx]}`
      },
    },
    legend: { data: ['预测价格', '置信区间'], textStyle: { color: '#8b8fa3', fontSize: 11 }, top: 0 },
    grid: { left: '8%', right: '4%', top: '15%', bottom: '12%' },
    xAxis: {
      type: 'category',
      data: times,
      axisLine: { lineStyle: { color: '#2a2d3a' } },
      axisLabel: { color: '#8b8fa3', fontSize: 10, rotate: 30 },
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: { lineStyle: { color: '#2a2d3a' } },
      axisLabel: { color: '#8b8fa3', fontSize: 11 },
    },
    series: [
      {
        name: '预测价格',
        type: 'line',
        data: predicted,
        smooth: true,
        lineStyle: { width: 2, color: '#f5c842', type: 'dashed' },
        symbol: 'none',
      },
      {
        name: '置信区间',
        type: 'line',
        data: upper,
        smooth: true,
        lineStyle: { opacity: 0 },
        symbol: 'none',
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(91, 141, 239, 0.25)' },
            { offset: 1, color: 'rgba(91, 141, 239, 0.05)' },
          ]),
        },
        stack: 'confidence',
      },
      {
        name: '置信区间',
        type: 'line',
        data: lower,
        smooth: true,
        lineStyle: { opacity: 0 },
        symbol: 'none',
        areaStyle: {
          color: 'rgba(15, 17, 23, 0.8)',
        },
        stack: 'confidence',
      },
    ],
  }
}

function initChart() {
  if (chart || !chartRef.value) return
  chart = echarts.init(chartRef.value)
  window.addEventListener('resize', () => chart?.resize())
}

function renderChart() {
  if (!props.forecast.forecast?.length) return
  if (!chart) {
    nextTick(() => {
      initChart()
      if (chart) chart.setOption(buildOption(), true)
    })
    return
  }
  chart.setOption(buildOption(), true)
}

watch(() => props.forecast, renderChart, { deep: true })

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', () => chart?.resize())
})
</script>

<style scoped>
.forecast-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.confidence-badge {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.confidence-badge.high {
  background: var(--color-up-bg);
  color: var(--color-up);
}

.confidence-badge.medium {
  color: var(--color-gold);
  background: var(--color-gold-dim);
}

.confidence-badge.low {
  background: var(--color-down-bg);
  color: var(--color-down);
}

.forecast-summary {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 14px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  width: fit-content;
}

.trend-badge.up {
  color: var(--color-up);
  background: var(--color-up-bg);
}

.trend-badge.down {
  color: var(--color-down);
  background: var(--color-down-bg);
}

.trend-badge.flat {
  color: var(--color-text-secondary);
  background: rgba(139, 143, 163, 0.1);
}

.trend-strength {
  font-size: 12px;
  opacity: 0.7;
}

.forecast-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.forecast-chart {
  width: 100%;
  height: 240px;
}
</style>
