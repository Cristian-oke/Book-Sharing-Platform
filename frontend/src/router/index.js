import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { isAuthenticated, token } from '../auth'


const isAdmin = () => {
  if (!token.value) return false
  try {
    const base64Url = token.value.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const decoded = JSON.parse(decodeURIComponent(atob(base64).split('').map(c => {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)}).join('')))
    return decoded.role === 'admin'
  } catch (e) {
    return false
  }
}

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
  },
  {
    path: '/admin/stats',
    name: 'AdminStats',
    component: () => import('../views/AdminStatsView.vue'), 
    meta: { requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAdmin) {
    if (isAuthenticated.value && isAdmin()) {
      next() 
    } else {
      alert("Acces interzis! Doar administratorii pot accesa această pagină.")
      next(isAuthenticated.value ? '/home' : '/login') 
    }
  } else {
    next()
  }
})

export default router