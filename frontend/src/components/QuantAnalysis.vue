<template>
  <div class="card quant-card">
    <div class="section-header">
      <h3>量化分析</h3>
      <span v-if="quant.current_price" class="quant-price">
        ¥{{ formatPrice(quant.current_price) }}
      </span>
    </div>

    <div v-if="loading" class="loading">计算中...</div>
    <template v-else-if="quant.signals">
      <!-- Signal Summary -->
      <div class="signal-row">
        <div
          v-for="signal in quant.signals"
          :key="signal.indicator"
          class="signal-chip"
          :class="signal.strength"
        >
          <span class="signal-name">{{ signal.indicator }}</span>
          <span class="signal-value">{{ signal.signal }}</span>
        </div>
      </div>

      <div class="quant-grid">
        <!-- Moving Averages -->
        <div class="quant-block">
          <h4>均线系统</h4>
          <div class="ma-row">
            <span class="ma-item ma5">MA5: {{ fmt(quant.ma?.ma5) }}</span>
            <span class="ma-item ma10">MA10: {{ fmt(quant.ma?.ma10) }}</span>
            <span class="ma-item ma20">MA20: {{ fmt(quant.ma?.ma20) }}</span>
          </div>
        </div>

        <!-- Bollinger Bands -->
        <div class="quant-block">
          <h4>布林带</h4>
          <div class="bb-values">
            <div class="bb-item"><span class="bb-label">上轨</span><span class="bb-val">{{ fmt(quant.bollinger?.upper) }}</span></div>
            <div class="bb-item"><span class="bb-label">中轨</span><span class="bb-val">{{ fmt(quant.bollinger?.middle) }}</span></div>
            <div class="bb-item"><span class="bb-label">下轨</span><span class="bb-val">{{ fmt(quant.bollinger?.lower) }}</span></div>
            <div class="bb-item"><span class="bb-label">带宽</span><span class="bb-val">{{ quant.bollinger?.width ?? '--' }}%</span></div>
          </div>
        </div>

        <!-- RSI -->
        <div class="quant-block">
          <h4>RSI (14)</h4>
          <div class="rsi-block">
            <div class="rsi-value" :class="rsiClass">{{ quant.rsi ?? '--' }}</div>
            <div class="rsi-bar">
              <div class="rsi-fill" :style="{ width: (quant.rsi || 0) + '%' }"></div>
            </div>
            <div class="rsi-labels">
              <span>0</span>
              <span>超卖 30</span>
              <span>超买 70</span>
              <span>100</span>
            </div>
          </div>
        </div>

        <!-- MACD -->
        <div class="quant-block">
          <h4>MACD</h4>
          <div class="macd-values">
            <div class="macd-item"><span class="macd-label">DIF</span><span class="macd-val">{{ fmt(quant.macd?.dif) }}</span></div>
            <div class="macd-item"><span class="macd-label">DEA</span><span class="macd-val">{{ fmt(quant.macd?.dea) }}</span></div>
            <div class="macd-item"><span class="macd-label">MACD柱</span><span class="macd-val" :class="macdVal > 0 ? 'up' : 'down'">{{ fmt(macdVal) }}</span></div>
          </div>
        </div>

        <!-- Volatility -->
        <div class="quant-block">
          <h4>波动率</h4>
          <div class="vol-values">
            <div class="vol-item"><span class="vol-label">日内</span><span class="vol-val">{{ quant.volatility?.daily ?? '--' }}%</span></div>
            <div class="vol-item"><span class="vol-label">年化</span><span class="vol-val">{{ quant.volatility?.annualized ?? '--' }}%</span></div>
          </div>
        </div>

        <!-- Momentum -->
        <div class="quant-block">
          <h4>动量</h4>
          <div class="mom-values">
            <div class="mom-item">
              <span class="mom-label">5周期</span>
              <span class="mom-val" :class="quant.momentum?.mom_5 >= 0 ? 'up' : 'down'">{{ fmtSigned(quant.momentum?.mom_5) }}</span>
            </div>
            <div class="mom-item">
              <span class="mom-label">10周期</span>
              <span class="mom-val" :class="quant.momentum?.mom_10 >= 0 ? 'up' : 'down'">{{ fmtSigned(quant.momentum?.mom_10) }}</span>
            </div>
            <div class="mom-item">
              <span class="mom-label">20周期</span>
              <span class="mom-val" :class="quant.momentum?.mom_20 >= 0 ? 'up' : 'down'">{{ fmtSigned(quant.momentum?.mom_20) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="empty-state">暂无量化数据，请先获取K线数据</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  quant: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
})

const macdVal = computed(() => {
  return props.quant.macd?.macd ?? 0
})

const rsiClass = computed(() => {
  const rsi = props.quant.rsi
  if (rsi == null) return ''
  if (rsi > 70) return 'overbought'
  if (rsi < 30) return 'oversold'
  return 'neutral'
})

function formatPrice(val) {
  if (val == null) return '--'
  return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function fmt(val) {
  if (val == null) return '--'
  return Number(val).toFixed(2)
}

function fmtSigned(val) {
  if (val == null) return '--'
  const n = Number(val)
  return (n >= 0 ? '+' : '') + n.toFixed(2)
}
</script>

<style scoped>
.quant-card {
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

.quant-price {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-gold);
}

/* Signal Chips */
.signal-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.signal-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 14px;
  border-radius: 8px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  gap: 2px;
}

.signal-chip.strong {
  border-color: var(--color-up);
}

.signal-chip.warning {
  border-color: var(--color-gold);
}

.signal-chip.weak,
.signal-chip.neutral {
  border-color: var(--color-border);
}

.signal-name {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.signal-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}

/* Grid Layout */
.quant-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.quant-block {
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  padding: 12px;
  border: 1px solid var(--color-border);
}

.quant-block h4 {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

/* Moving Averages */
.ma-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.ma-item {
  font-size: 13px;
  font-weight: 500;
}

.ma-item.ma5 { color: #f5c842; }
.ma-item.ma10 { color: #5b8def; }
.ma-item.ma20 { color: #a855f7; }

/* Bollinger Bands */
.bb-values {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bb-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.bb-label { color: var(--color-text-secondary); }
.bb-val { font-weight: 600; }

/* RSI */
.rsi-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rsi-value {
  font-size: 24px;
  font-weight: 700;
}

.rsi-value.overbought { color: var(--color-down); }
.rsi-value.oversold { color: var(--color-up); }
.rsi-value.neutral { color: var(--color-text); }

.rsi-bar {
  height: 6px;
  background: var(--color-surface-hover);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.rsi-fill {
  height: 100%;
  border-radius: 3px;
  background: var(--color-primary);
  transition: width 0.3s;
}

.rsi-bar::before {
  content: '';
  position: absolute;
  left: 30%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(239, 83, 80, 0.5);
}

.rsi-bar::after {
  content: '';
  position: absolute;
  left: 70%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(38, 166, 154, 0.5);
}

.rsi-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--color-text-secondary);
}

/* MACD */
.macd-values {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.macd-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.macd-label { color: var(--color-text-secondary); }
.macd-val { font-weight: 600; }
.macd-val.up { color: var(--color-up); }
.macd-val.down { color: var(--color-down); }

/* Volatility */
.vol-values {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.vol-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.vol-label { color: var(--color-text-secondary); }
.vol-val { font-weight: 600; }

/* Momentum */
.mom-values {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mom-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.mom-label { color: var(--color-text-secondary); }
.mom-val { font-weight: 600; }
.mom-val.up { color: var(--color-up); }
.mom-val.down { color: var(--color-down); }

/* Responsive */
@media (max-width: 768px) {
  .quant-grid {
    grid-template-columns: 1fr;
  }

  .signal-row {
    gap: 6px;
  }
}
</style>
