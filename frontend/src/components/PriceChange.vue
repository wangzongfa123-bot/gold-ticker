<template>
  <span class="price-change" :class="isUp ? 'up' : 'down'">
    {{ isUp ? '+' : '' }}{{ formatNum(change) }}
    ({{ isUp ? '+' : '' }}{{ formatNum(percent) }}%)
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  change: Number,
  percent: Number,
})

const isUp = computed(() => (props.change || 0) >= 0)

function formatNum(val) {
  if (val == null) return '0.00'
  return Number(val).toFixed(2)
}
</script>
