<template>
  <div class="alert-list">
    <div v-if="!alerts.length" class="empty-state">
      暂无预警规则，请在上方创建。
    </div>
    <div v-for="alert in alerts" :key="alert.id" class="alert-item">
      <div class="alert-item-info">
        <span class="alert-item-name">{{ alert.name }}</span>
        <span class="alert-item-detail">
          {{ alert.condition === 'above' ? '>=' : '<=' }}
          ¥{{ alert.threshold }} 元/克
          <template v-if="alert.triggered_at">
            &middot; 已触发 {{ formatTime(alert.triggered_at) }}
          </template>
        </span>
      </div>
      <div class="alert-item-actions">
        <label class="toggle">
          <input type="checkbox" :checked="alert.is_active" @change="toggleAlert(alert)" />
          <span class="toggle-slider"></span>
        </label>
        <button class="btn btn-danger btn-sm" @click="removeAlert(alert.id)">删除</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAlertStore } from '../stores/alert'

const alertStore = useAlertStore()
const alerts = computed(() => alertStore.alerts)

function toggleAlert(alert) {
  alertStore.updateAlert(alert.id, { is_active: !alert.is_active })
}

function removeAlert(id) {
  alertStore.deleteAlert(id)
}

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleString()
}
</script>
