import { createRouter, createWebHistory } from 'vue-router'
import PingView from '@/views/Ping.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/ping',
      name: 'ping',
      component: PingView
    }
  ]
})

export default router
