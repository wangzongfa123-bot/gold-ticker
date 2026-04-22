<template>
  <div class="card geo-card">
    <div class="section-header">
      <h3>宏观与政治因素</h3>
      <span class="update-time">{{ updateTime }}</span>
    </div>

    <div class="geo-intro">
      以下因素综合影响黄金价格走势，标注了对金价的影响方向及强度。
    </div>

    <div class="factor-list">
      <div
        v-for="factor in factors"
        :key="factor.name"
        class="factor-item"
      >
        <div class="factor-left">
          <span class="factor-name">{{ factor.name }}</span>
          <span class="factor-desc">{{ factor.desc }}</span>
        </div>
        <div class="factor-right">
          <span class="impact-badge" :class="factor.impact">
            {{ impactLabel[factor.impact] }}
          </span>
          <span class="direction" :class="factor.direction">
            {{ directionLabel[factor.direction] }}
          </span>
        </div>
      </div>
    </div>

    <div class="geo-disclaimer">
      以上为基于历史经验的市场分析，不构成投资建议。
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const updateTime = computed(() => {
  return new Date().toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
})

const impactLabel = {
  high: '高影响',
  medium: '中影响',
  low: '低影响',
}

const directionLabel = {
  bullish: '看涨',
  bearish: '看跌',
  neutral: '中性',
}

const factors = [
  {
    name: '美联储利率政策',
    desc: '利率上升增加持有黄金的机会成本，压低金价；降息周期则反之。当前关注加息/降息预期变化。',
    impact: 'high',
    direction: 'bullish',
  },
  {
    name: '地缘政治冲突',
    desc: '中东局势、俄乌冲突等地缘风险推动避险资金流入黄金，短期提振金价。',
    impact: 'high',
    direction: 'bullish',
  },
  {
    name: '美元指数走势',
    desc: '黄金以美元计价，美元走强通常压制金价，美元走弱则支撑金价。',
    impact: 'high',
    direction: 'bearish',
  },
  {
    name: '全球央行购金',
    desc: '多国央行持续增持黄金储备，尤其是新兴市场国家去美元化趋势，中长期支撑金价。',
    impact: 'medium',
    direction: 'bullish',
  },
  {
    name: '美国通胀数据 (CPI/PCE)',
    desc: '通胀高企时黄金作为抗通胀工具受追捧，但若引发激进加息则形成反向压力。',
    impact: 'medium',
    direction: 'neutral',
  },
  {
    name: '中美经贸关系',
    desc: '贸易摩擦升级推升不确定性，提振黄金避险需求；关系缓和则风险偏好回升。',
    impact: 'medium',
    direction: 'bullish',
  },
  {
    name: '全球经济衰退预期',
    desc: '经济放缓预期升温时，资金从风险资产转向黄金等避险资产。',
    impact: 'medium',
    direction: 'bullish',
  },
  {
    name: '原油价格波动',
    desc: '油价上涨推升通胀预期，间接支撑金价；油价下跌则减轻通胀压力。',
    impact: 'low',
    direction: 'neutral',
  },
  {
    name: '比特币等加密资产',
    desc: '部分资金将比特币视为"数字黄金"，加密资产走强可能分流黄金资金。',
    impact: 'low',
    direction: 'bearish',
  },
  {
    name: '国内货币政策与人民币汇率',
    desc: '人民币贬值推升以人民币计价的黄金价格；国内流动性宽松也有助于金价上涨。',
    impact: 'medium',
    direction: 'bullish',
  },
]
</script>

<style scoped>
.geo-card {
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

.update-time {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.geo-intro {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.factor-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.factor-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px 14px;
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  gap: 12px;
}

.factor-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.factor-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.factor-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.factor-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.impact-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.impact-badge.high {
  background: rgba(239, 83, 80, 0.15);
  color: #ef5350;
}

.impact-badge.medium {
  color: var(--color-gold);
  background: var(--color-gold-dim);
}

.impact-badge.low {
  background: rgba(139, 143, 163, 0.15);
  color: var(--color-text-secondary);
}

.direction {
  font-size: 12px;
  font-weight: 600;
}

.direction.bullish {
  color: var(--color-up);
}

.direction.bearish {
  color: var(--color-down);
}

.direction.neutral {
  color: var(--color-text-secondary);
}

.geo-disclaimer {
  font-size: 11px;
  color: var(--color-text-secondary);
  opacity: 0.7;
  padding-top: 4px;
  border-top: 1px solid var(--color-border);
}
</style>
