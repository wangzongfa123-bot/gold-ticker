import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_BACKEND_HTTP || 'http://localhost:8001'
  const wsTarget =
    env.VITE_BACKEND_WS || apiTarget.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')

  return {
    plugins: [vue()],
    server: {
      proxy: {
        '/api': apiTarget,
        '/ws': {
          target: wsTarget,
          ws: true,
        },
      },
    },
  }
})
