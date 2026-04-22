<template>
  <div ref="chartRef" style="width: 100%; height: 360px;"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, default: () => [] },
  interval: { type: String, default: '1h' },
})

const chartRef = ref(null)
let chart = null

function formatLabel(dt, interval) {
  const hh = String(dt.getHours()).padStart(2, '0')
  const mm = String(dt.getMinutes()).padStart(2, '0')
  const M = dt.getMonth() + 1
  const D = dt.getDate()
  if (interval === '1d') {
    return `${dt.getFullYear()}/${M}/${D}`
  }
  if (interval === '5m' || interval === '15m') {
    return `${hh}:${mm}`
  }
  return `${M}/${D} ${hh}:${mm}`
}

function buildOption(data) {
  const times = data.map(d => formatLabel(new Date(d.timestamp), props.interval))
  const prices = data.map(d => d.close || d.price_cny)

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a1d28',
      borderColor: '#2a2d3a',
      textStyle: { color: '#e4e6eb' },
    },
    grid: { left: '8%', right: '4%', top: '8%', bottom: '18%' },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#2a2d3a' } },
      axisLabel: { color: '#8b8fa3', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: { lineStyle: { color: '#2a2d3a' } },
      axisLabel: { color: '#8b8fa3' },
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
    ],
    series: [
      {
        name: '价格',
        type: 'line',
        data: prices,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#f5c842' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 200, 66, 0.3)' },
            { offset: 1, color: 'rgba(245, 200, 66, 0.02)' },
          ]),
        },
      },
    ],
  }
}

function renderChart() {
  if (!chart || !props.data.length) return
  chart.setOption(buildOption(props.data), true)
}

onMounted(() => {
  chart = echarts.init(chartRef.value)
  renderChart()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', () => chart?.resize())
})

watch(() => props.data, renderChart, { deep: true })
watch(() => props.interval, renderChart)
</script>
