<template>
  <div class="funds-page">
    <div class="page-header">
      <h2>基金推荐</h2>
      <p class="page-desc">精选黄金、A股热门、海外ETF基金，综合配置建议</p>
    </div>

    <div class="card fund-section">
      <div class="chart-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          :class="{ active: selectedCategory === tab.value }"
          @click="switchCategory(tab.value)"
        >
          {{ tab.label }}
        </button>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="funds.length" class="fund-grid">
        <FundCard v-for="fund in funds" :key="fund.code" :fund="fund" />
      </div>
      <div v-else class="empty-state">暂无基金数据</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFundStore } from '../stores/fund'
import FundCard from '../components/FundCard.vue'

const fundStore = useFundStore()
const funds = ref([])
const loading = ref(false)
const selectedCategory = ref('')

const tabs = [
  { value: '', label: '全部' },
  { value: 'gold', label: '黄金' },
  { value: 'a_share', label: 'A股热门' },
  { value: 'overseas', label: '海外' },
]

async function switchCategory(category) {
  selectedCategory.value = category
  await fundStore.fetchFunds(category)
  funds.value = fundStore.funds
}

onMounted(async () => {
  await fundStore.fetchFunds()
  funds.value = fundStore.funds
})
</script>

<style scoped>
.funds-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 4px;
}

.page-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.fund-section {
  display: flex;
  flex-direction: column;
}

.fund-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px;
}

@media (max-width: 768px) {
  .fund-grid {
    grid-template-columns: 1fr;
  }
}
</style>
