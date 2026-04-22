<template>
  <div ref="chartRef" style="width: 100%; height: 160px;"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Object, default: null },
})

const chartRef = ref(null)
let chart = null

function buildOption(data) {
  if (!data?.navs?.length) return {}
  const navs = [...data.navs].reverse()
  const dates = navs.map(n => n.nav_date.slice(5))
  const values = navs.map(n => n.nav)
  const dailyReturns = navs.map(n => n.daily_return || 0)
  const colors = dailyReturns.map(r => r >= 0 ? '#26a69a' : '#ef5350')

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a1d28',
      borderColor: '#2a2d3a',
      textStyle: { color: '#e4e6eb' },
    },
    grid: { left: '4%', right: '4%', top: '4%', bottom: '4%' },
    xAxis: {
      type: 'category',
      data: dates,
      show: false,
    },
    yAxis: {
      type: 'value',
      scale: true,
      show: false,
    },
    series: [
      {
        type: 'bar',
        data: colors.map((c, i) => ({ value: dailyReturns[i], itemStyle: { color: c } })),
        barWidth: '60%',
      },
    ],
  }
}

function renderChart() {
  if (!chart) return
  if (!props.data?.navs?.length) return
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
</script>
