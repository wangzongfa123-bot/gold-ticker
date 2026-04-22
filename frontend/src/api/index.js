import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export const priceApi = {
  getCurrent: () => api.get('/prices/current'),
  getHistory: (params) => api.get('/prices/history', { params }),
  getKline: (params) => api.get('/prices/kline', { params }),
  getStats: () => api.get('/prices/stats'),
  getForecast: (params) => api.get('/prices/forecast', { params }),
  getQuant: () => api.get('/prices/quant'),
}

export const alertApi = {
  list: () => api.get('/alerts/'),
  create: (data) => api.post('/alerts/', data),
  update: (id, data) => api.put(`/alerts/${id}`, data),
  delete: (id) => api.delete(`/alerts/${id}`),
}

export const fundApi = {
  list: (category) => api.get('/funds/list', { params: { category } }),
  getNav: (code, limit = 30) => api.get(`/funds/${code}/nav`, { params: { limit } }),
  getAnalysis: (code) => api.get(`/funds/${code}/analysis`),
}

export default api
