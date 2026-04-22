<template>
  <div class="card fund-card" :class="{ expanded: isExpanded }" @click="toggle">
    <div class="fund-header">
      <div class="fund-title">
        <span class="fund-name">{{ fund.name }}</span>
        <span class="fund-code">{{ fund.code }}</span>
      </div>
      <span class="category-badge" :class="fund.category">
        {{ categoryLabel[fund.category] }}
      </span>
    </div>

    <div v-if="analysis" class="fund-summary">
      <div class="fund-metric">
        <span class="metric-label">最新净值</span>
        <span class="metric-value">{{ fmt(analysis.current_nav) }}</span>
      </div>
      <div class="fund-metric">
        <span class="metric-label">日涨跌</span>
        <span class="metric-value" :class="analysis.daily_return >= 0 ? 'up' : 'down'">
          {{ fmt(analysis.daily_return) }}%
        </span>
      </div>
      <div class="fund-metric">
        <span class="metric-label">5日涨幅</span>
        <span class="metric-value" :class="analysis.momentum_5d >= 0 ? 'up' : 'down'">
          {{ fmt(analysis.momentum_5d) }}%
        </span>
      </div>
      <div class="fund-metric">
        <span class="metric-label">20日涨幅</span>
        <span class="metric-value" :class="analysis.momentum_20d >= 0 ? 'up' : 'down'">
          {{ fmt(analysis.momentum_20d) }}%
        </span>
      </div>
    </div>

    <div v-if="isExpanded && navData" class="fund-expanded">
      <FundNavChart :data="navData" />
      <div class="fund-reason">
        <span class="reason-label">推荐理由：</span>
        <span class="reason-text">{{ analysis?.recommendation_reason || '' }}</span>
      </div>
      <div class="trade-calculator">
        <div class="trade-header">
          <span class="reason-label">交易计算：</span>
          <span class="lot-info">每手 {{ analysis?.lot_size }} 股，每手约 ¥{{ fmt(analysis?.lot_price) }}</span>
        </div>
        <div class="trade-input-row">
          <input v-model.number="tradeAmount" type="number" placeholder="输入金额" class="trade-input" />
          <span class="trade-result" v-if="canBuy > 0">
            可买 <strong>{{ canBuy }}</strong> 手，花费 ¥{{ fmt(totalCost) }}，剩余 ¥{{ fmt(tradeAmount - totalCost) }}
          </span>
          <span class="trade-result trade-empty" v-else-if="tradeAmount > 0 && canBuy === 0">
            金额不足 1 手
          </span>
        </div>
        <div class="trade-quick">
          <button @click.stop="tradeAmount = 1000">1千</button>
          <button @click.stop="tradeAmount = 5000">5千</button>
          <button @click.stop="tradeAmount = 10000">1万</button>
          <button @click.stop="tradeAmount = 50000">5万</button>
        </div>
      </div>
    </div>

    <div class="fund-hint">
      {{ isExpanded ? '点击收起' : '点击展开详情' }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useFundStore } from '../stores/fund'
import FundNavChart from './FundNavChart.vue'

const props = defineProps({
  fund: { type: Object, required: true },
})

const fundStore = useFundStore()
const isExpanded = ref(false)
const navData = ref(null)
const analysis = ref(null)
const tradeAmount = ref(null)

const canBuy = computed(() => {
  if (!tradeAmount.value || !analysis.value?.lot_price) return 0
  return Math.floor(tradeAmount.value / analysis.value.lot_price)
})

const totalCost = computed(() => {
  return canBuy.value * (analysis.value?.lot_price || 0)
})

const categoryLabel = {
  gold: '黄金',
  a_share: 'A股热门',
  overseas: '海外',
}

async function loadData() {
  if (analysis.value) return
  analysis.value = await fundStore.fetchAnalysis(props.fund.code)
  navData.value = await fundStore.fetchNav(props.fund.code)
}

function toggle() {
  isExpanded.value = !isExpanded.value
  if (isExpanded.value) {
    loadData()
  }
}

function fmt(val) {
  if (val == null) return '--'
  return Number(val).toFixed(2)
}
</script>

<style scoped>
.fund-card {
  cursor: pointer;
  transition: all 0.2s;
}

.fund-card:hover {
  background: var(--color-surface-hover);
}

.fund-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.fund-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.fund-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.fund-code {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-family: monospace;
}

.category-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.category-badge.gold {
  background: var(--color-gold-dim);
  color: var(--color-gold);
}

.category-badge.a_share {
  background: rgba(91, 141, 239, 0.15);
  color: #5b8def;
}

.category-badge.overseas {
  background: rgba(38, 166, 154, 0.15);
  color: #26a69a;
}

.fund-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.fund-metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px;
  background: var(--color-bg);
  border-radius: 6px;
}

.metric-label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.metric-value.up { color: var(--color-up); }
.metric-value.down { color: var(--color-down); }

.fund-expanded {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.fund-reason {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.reason-label {
  font-weight: 600;
  color: var(--color-gold);
}

.fund-hint {
  text-align: center;
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-top: 8px;
  opacity: 0.6;
}

.trade-calculator {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.trade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
}

.lot-info {
  color: var(--color-gold);
  font-weight: 500;
}

.trade-input-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.trade-input {
  width: 120px;
  padding: 6px 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg);
  color: var(--color-text);
  font-size: 13px;
  outline: none;
}

.trade-input:focus {
  border-color: var(--color-gold);
}

.trade-result {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.trade-result strong {
  color: var(--color-gold);
  font-size: 15px;
}

.trade-result.trade-empty {
  color: var(--color-text-secondary);
  opacity: 0.7;
}

.trade-quick {
  display: flex;
  gap: 6px;
}

.trade-quick button {
  padding: 4px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.trade-quick button:hover {
  background: var(--color-gold);
  color: var(--color-bg);
  border-color: var(--color-gold);
}
</style>
