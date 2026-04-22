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
  const categoryData = data.map(d => formatLabel(new Date(d.timestamp), props.interval))
  const ohlc = data.map(d => [d.open, d.close, d.low, d.high])
  const closes = data.map(d => d.close)

  // Simple MA5
  const ma5 = closes.map((_, i) => {
    if (i < 4) return null
    const sum = closes.slice(i - 4, i + 1).reduce((a, b) => a + b, 0)
    return +(sum / 5).toFixed(2)
  })

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#1a1d28',
      borderColor: '#2a2d3a',
      textStyle: { color: '#e4e6eb' },
    },
    grid: { left: '8%', right: '4%', top: '10%', bottom: '18%' },
    xAxis: {
      type: 'category',
      data: categoryData,
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
      { type: 'inside', start: 60, end: 100 },
      { type: 'slider', start: 60, end: 100, height: 20, bottom: 5, borderColor: '#2a2d3a', fillerColor: 'rgba(91,141,239,0.15)' },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: ohlc,
        itemStyle: {
          color: '#26a69a',
          color0: '#ef5350',
          borderColor: '#26a69a',
          borderColor0: '#ef5350',
        },
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma5,
        smooth: true,
        lineStyle: { width: 1, color: '#f5c842' },
        symbol: 'none',
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
