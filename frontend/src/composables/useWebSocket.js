import { ref, onUnmounted } from 'vue'
import { usePriceStore } from '../stores/price'
import { useAlertStore } from '../stores/alert'

export function useWebSocket() {
  const isConnected = ref(false)
  let ws = null
  let reconnectTimer = null
  let pingTimer = null
  let reconnectDelay = 1000

  function getWsUrl() {
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${proto}//${location.host}/ws/prices`
  }

  function connect() {
    if (ws && ws.readyState === WebSocket.OPEN) return

    ws = new WebSocket(getWsUrl())

    ws.onopen = () => {
      isConnected.value = true
      reconnectDelay = 1000
      startPing()
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'price_update') {
          const priceStore = usePriceStore()
          priceStore.updatePrice(msg.data)
        } else if (msg.type === 'alert_triggered') {
          const alertStore = useAlertStore()
          alertStore.addTriggeredAlert(msg.data)
          showBrowserNotification(msg.data)
        }
      } catch (e) {
        // ignore non-JSON messages (like "pong")
      }
    }

    ws.onclose = () => {
      isConnected.value = false
      stopPing()
      scheduleReconnect()
    }

    ws.onerror = () => {
      ws.close()
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      reconnectDelay = Math.min(reconnectDelay * 2, 30000)
      connect()
    }, reconnectDelay)
  }

  function startPing() {
    stopPing()
    pingTimer = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send('ping')
      }
    }, 30000)
  }

  function stopPing() {
    if (pingTimer) {
      clearInterval(pingTimer)
      pingTimer = null
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    stopPing()
    if (ws) {
      ws.close()
      ws = null
    }
  }

  function showBrowserNotification(alertData) {
    if (Notification.permission === 'granted') {
      const cond = alertData.condition === 'above' ? '上穿' : '下穿'
      new Notification('黄金价格预警', {
        body: `${alertData.name}: 价格${cond} ¥${alertData.threshold} (当前: ¥${alertData.current_price})`,
        icon: '/favicon.ico',
      })
    }
  }

  onUnmounted(disconnect)

  return { isConnected, connect, disconnect }
}
