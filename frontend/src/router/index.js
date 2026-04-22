import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import AlertsView from '../views/AlertsView.vue'
import FundsView from '../views/FundsView.vue'

const routes = [
  { path: '/', name: 'dashboard', component: DashboardView },
  { path: '/alerts', name: 'alerts', component: AlertsView },
  { path: '/funds', name: 'funds', component: FundsView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
