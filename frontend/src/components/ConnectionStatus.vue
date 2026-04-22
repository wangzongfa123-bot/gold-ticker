<template>
  <div class="connection-status" :title="connected ? 'Connected' : 'Disconnected'">
    <span class="connection-dot" :class="connected ? 'connected' : 'disconnected'"></span>
  </div>
</template>

<script setup>
defineProps({
  connected: Boolean,
})
</script>
