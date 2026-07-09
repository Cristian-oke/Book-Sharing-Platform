import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/home',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/book/:id',
    name: 'Detalii Carte',
    component: () => import('../views/BookDetailsView.vue')
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router