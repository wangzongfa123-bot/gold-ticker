import { ref } from 'vue'

export function useNotification() {
  const permission = ref(Notification.permission)

  async function requestPermission() {
    if (Notification.permission === 'default') {
      const result = await Notification.requestPermission()
      permission.value = result
    }
  }

  return { permission, requestPermission }
}
