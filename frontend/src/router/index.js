import { createRouter, createWebHistory } from 'vue-router'
import ChatPage from '../pages/ChatPage.vue'
import LecturePage from '../pages/LecturePage.vue'
import SlidePage from '../pages/SlidePage.vue'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: ChatPage
  },
  {
    path: '/chat/:sessionId?',
    name: 'ChatSession',
    component: ChatPage,
    props: true
  },
  {
    path: '/lectures',
    name: 'Lectures',
    component: LecturePage
  },
  {
    path: '/slides',
    name: 'Slides',
    component: SlidePage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
