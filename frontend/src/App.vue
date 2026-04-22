<template>
  <div class="app">
    <nav class="navbar">
      <div class="navbar-brand">
        <span>Au</span> 黄金监控
      </div>
      <div class="navbar-links">
        <router-link to="/">行情</router-link>
        <router-link to="/alerts">预警</router-link>
        <router-link to="/funds">基金</router-link>
      </div>
      <div class="navbar-right">
        <ConnectionStatus :connected="isConnected" />
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
    <AlertNotification />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useWebSocket } from './composables/useWebSocket'
import { useNotification } from './composables/useNotification'
import ConnectionStatus from './components/ConnectionStatus.vue'
import AlertNotification from './components/AlertNotification.vue'

const { isConnected, connect } = useWebSocket()
const { requestPermission } = useNotification()

onMounted(() => {
  connect()
  requestPermission()
})
</script>
