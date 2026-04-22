<template>
  <div class="alert-toast-container" v-if="triggeredAlerts.length">
    <div v-for="(alert, index) in triggeredAlerts" :key="index" class="alert-toast">
      <div>
        <div style="font-weight: 600; font-size: 14px; color: var(--color-gold);">
          Alert Triggered
        </div>
        <div style="font-size: 13px; color: var(--color-text-secondary); margin-top: 4px;">
          {{ alert.name }}: price {{ alert.condition }} {{ alert.threshold }}
          (current: {{ alert.current_price }})
        </div>
      </div>
      <button class="alert-toast-close" @click="dismiss(index)">&times;</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAlertStore } from '../stores/alert'

const alertStore = useAlertStore()
const triggeredAlerts = computed(() => alertStore.triggeredAlerts)

function dismiss(index) {
  alertStore.dismissTriggered(index)
}
</script>
