import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/profile',
    name: 'Profil Utilizator',
    component: () => import('../views/ProfileView.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue')
  },
  {
    path: '/history',
    name: 'Istoric Împrumuturi',
    component: () => import('../views/HistoryView.vue')
  },
  {
    path: '/login',
    name: 'Autentificare',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/user/:id',
    name: 'UserProfile',
    component: () => import('../views/UserProfileView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router