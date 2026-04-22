<template>
  <div>
    <h2 style="margin-bottom: 16px; font-size: 20px;">价格预警</h2>
    <AlertForm />
    <div class="card" style="margin-top: 20px;">
      <div v-if="loading" class="loading">加载中...</div>
      <AlertList v-else />
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useAlertStore } from '../stores/alert'
import AlertForm from '../components/AlertForm.vue'
import AlertList from '../components/AlertList.vue'

const alertStore = useAlertStore()
const loading = computed(() => alertStore.loading)

onMounted(() => {
  alertStore.fetchAlerts()
})
</script>
