<template>
  <div class="card price-card">
    <div class="price-main">
      <span class="price-value">¥{{ formatPrice(currentPrice.price_cny) }}</span>
      <span class="price-currency">元/克</span>
      <PriceChange
        v-if="currentPrice.change != null"
        :change="currentPrice.change"
        :percent="currentPrice.change_percent"
      />
    </div>
    <div class="price-source">数据来源：招商银行 Au99.99</div>
    <div class="price-meta">
      <div class="price-meta-item" v-if="currentPrice.high_24h">
        <span class="price-meta-label">24h 最高</span>
        <span class="price-meta-value">¥{{ formatPrice(currentPrice.high_24h) }}</span>
      </div>
      <div class="price-meta-item" v-if="currentPrice.low_24h">
        <span class="price-meta-label">24h 最低</span>
        <span class="price-meta-value">¥{{ formatPrice(currentPrice.low_24h) }}</span>
      </div>
      <div class="price-meta-item" v-if="currentPrice.timestamp">
        <span class="price-meta-label">更新时间</span>
        <span class="price-meta-value">{{ formatTime(currentPrice.timestamp) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePriceStore } from '../stores/price'
import PriceChange from './PriceChange.vue'

const priceStore = usePriceStore()
const currentPrice = computed(() => priceStore.currentPrice)

function formatPrice(val) {
  if (!val) return '0.00'
  return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleString('zh-CN')
}
</script>
