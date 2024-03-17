import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/Home.vue'
import LobbyView from '@/views/Lobby.vue'
import PingView from '@/views/Ping.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/lobby/:id',
      name: 'lobby',
      component: LobbyView
    },
    {
      path: '/ping',
      name: 'ping',
      component: PingView
    }
  ]
})

export default router
