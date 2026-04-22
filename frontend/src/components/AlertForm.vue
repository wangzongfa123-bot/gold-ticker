<template>
  <form class="card alert-form" @submit.prevent="handleSubmit">
    <div class="form-group">
      <label>名称</label>
      <input v-model="form.name" placeholder="例如: 金价突破1000" required />
    </div>
    <div class="form-group">
      <label>条件</label>
      <select v-model="form.condition">
        <option value="above">上穿 (>=)</option>
        <option value="below">下穿 (<=)</option>
      </select>
    </div>
    <div class="form-group">
      <label>阈值 (元/克)</label>
      <input v-model.number="form.threshold" type="number" step="0.01" required />
    </div>
    <button type="submit" class="btn btn-primary" :disabled="loading">
      {{ loading ? '创建中...' : '创建预警' }}
    </button>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAlertStore } from '../stores/alert'

const alertStore = useAlertStore()
const loading = ref(false)

const form = reactive({
  name: '',
  condition: 'above',
  threshold: 0,
})

async function handleSubmit() {
  if (!form.name || !form.threshold) return
  loading.value = true
  try {
    await alertStore.createAlert({ ...form })
    form.name = ''
    form.threshold = 0
  } finally {
    loading.value = false
  }
}
</script>
