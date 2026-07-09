<script setup>
import { isAuthenticated, logout } from './auth'
import { useRouter } from 'vue-router'

const router = useRouter()

const handleAuthClick = () => {
  if (isAuthenticated.value) {
    logout()
    router.push('/home')
  } else {
    router.push('/login')
  }
}
</script>

<template>
  <div id="app-layout">
    <nav class="navbar">
      <div class="nav-left">
        <router-link to="/home">📚 Catalog Cărți</router-link> 
        <router-link to="/dashboard">💻 Dashboard</router-link> 
        <router-link to="/history">📜 Istoric</router-link> 
        <router-link to="/profile">👤 Profilul Meu</router-link>
      </div>

      <div class="nav-right">
        <button class="auth-nav-btn" :class="{ 'logged-in': isAuthenticated }" @click="handleAuthClick">
          {{ isAuthenticated ? '🛑 Deconectare' : '🔐 Autentificare' }}
        </button>
      </div>
    </nav>

    <main class="content">
      <router-view></router-view> 
    </main>
  </div>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 20px;
}

.nav-left a {
  margin-right: 20px;
  text-decoration: none;
  color: #2c3e50;
  font-weight: bold;
}

.nav-left a.router-link-exact-active {
  color: #42b983;
}

.auth-nav-btn {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.auth-nav-btn.logged-in {
  background-color: #e74c3c;
}

.auth-nav-btn:hover {
  opacity: 0.9;
}

.content {
  padding: 0 20px;
}
</style>