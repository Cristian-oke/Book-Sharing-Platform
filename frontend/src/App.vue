<script setup>
import { isAuthenticated,token, logout } from './auth'
import { useRouter } from 'vue-router'
import {computed} from 'vue'

const router = useRouter()

const isAdmin = computed(() => {
  if (!token.value) return false
  try {
    const base64Url = token.value.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    const decoded = JSON.parse(jsonPayload)
    
    return decoded.role === 'admin'
  } catch (error) {
    console.error("Eroare la verificarea rolului de admin:", error)
    return false
  }
})

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
      <div class="nav-left"> <!-- home dashboard istoric profilul meu admin-->
        <router-link to="/home">𝘏𝘰𝘮𝘦</router-link>
        <router-link to="/dashboard">𝘋𝘢𝘴𝘩𝘣𝘰𝘢𝘳𝘥</router-link>
        <router-link to="/history">𝘐𝘴𝘵𝘰𝘳𝘪𝘤</router-link>
        <router-link to="/profile">𝘗𝘳𝘰𝘧𝘪𝘭𝘶𝘭 𝘔𝘦𝘶</router-link>
        <router-link v-if="isAuthenticated && isAdmin" to="/admin/stats">𝘈𝘥𝘮𝘪𝘯</router-link>
      </div>

    
  <button class="auth-badge-btn" :class="{ 'is-logged-in': isAuthenticated }" @click="handleAuthClick">
  <!-- cerc stanga cu efect glossy -->
  <div class="badge-icon-circle">
    <!-- lacat deschis -->
    <svg v-if="!isAuthenticated" class="lock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
      <path d="M7 11V7a5 5 0 0 1 9.9-1"></path>
    </svg>

    <!-- lacat inchis -->
    <svg v-else class="lock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
      <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
    </svg>
  </div>

  <!-- deconectare autentificare -->
  <span class="badge-text">
    {{ isAuthenticated ? '𝘋𝘌𝘊𝘖𝘕𝘌𝘊𝘛𝘈𝘙𝘌' : '𝘈𝘜𝘛𝘌𝘕𝘛𝘐𝘍𝘐𝘊𝘈𝘙𝘌' }} 
  </span>
</button>

    </nav>

    <main class="content">
      <router-view></router-view> 
    </main>
  </div>
</template>

<style scoped>

.navbar {
  position: sticky;    
  top: 10px;               
  z-index: 1000;         
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 50px;
  background-color: #dfdcdc;
  border-bottom: 1px solid #e2e8f0;
  border-radius: 999px;    
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); /* umbra la scroll */
  margin-bottom: 20px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 9px; 
  margin-left: 20px;
}

.nav-left a {
  position: relative;
  text-decoration: none;
  background-color: #1e1e1e;
  color: #ffffff;
  
  font-weight: 600;
  font-size: 0.95rem;
  padding: 8px 18px;
  border-radius: 999px;
  display: flex;
  align-items: center;

  /* tranzitie pentru ridicarea butonului si schimbarea culorii */
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),background-color 0.25s ease,color 0.25s ease;
}

.nav-left a::after {
  content: '';
  position: absolute;
  bottom: 5px;
  left: 20%;        
  width: 60%;
  height: 2px;
  background-color: #eab308;
  border-radius: 2px;
  
  /*punctul de pornire al expansiunii este centrul */
  transform-origin: center;
  transform: scaleX(0);  /*invizibila in stare normala */
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);/* extindere si intindere fluida*/
}

.nav-left a:hover:not(.router-link-active) {
  background-color: #2b2619;
  color: #ffffff;  
  transform: translateY(-3px);
}

.nav-left a:hover:not(.router-link-active)::after {
  transform: scaleX(1); 
}

/* starea activa */
.nav-left a.router-link-active {
  background-color: #ffffff !important;
  color: #000000 !important;
  font-weight: 700;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  transform: none; /* Pagina activă rămâne ancorată jos */
}

.nav-left a.router-link-active::after {
  display: none;
}

.auth-badge-btn {
  display: inline-flex;
  align-items: center;
  background-color: #1e1e1e;    
  border: 1px solid #2d2d2d;
  border-radius: 999px;
  padding: 2px 14px 2px 2px; 
  cursor: pointer;
  position: relative;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  margin-right: 20px;
}

/* cercul pentru badge */
.badge-icon-circle {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7d7d7d 0%, #4a4a4a 100%);
  border: 2px solid #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: -4px;            /* suprapunere peste buton */
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.4),
              0 2px 4px rgba(0, 0, 0, 0.4);
  transition: transform 0.25s ease, background 0.25s ease;
}

/*reflexia glossy proportionala */
.badge-icon-circle::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.45), rgba(255, 255, 255, 0.05));
  border-radius: 50% 50% 0 0;
  pointer-events: none;
}

.lock-icon {
  width: 16px;
  height: 16px;
  color: #ffffff;
  filter: drop-shadow(0px 1px 1px rgba(0, 0, 0, 0.8));
  z-index: 2;
  transition: transform 0.2s ease;
}

.badge-text {
  color: #ffffff;
  font-weight: 700;
  font-size: 0.85rem;      
  letter-spacing: 0.6px;
  margin-left: 8px;
  font-family: system-ui, -apple-system, sans-serif;
  text-transform: uppercase;
}

.auth-badge-btn:hover {
  background-color: #2b2619; 
  transform: translateY(-3px);
}

.auth-badge-btn:hover .badge-icon-circle {
  background: linear-gradient(135deg, #949494 0%, #5a5a5a 100%);
}

.auth-badge-btn:hover .lock-icon {
  transform: scale(1.1);
}

.auth-badge-btn.is-logged-in:hover .badge-icon-circle {
  background: linear-gradient(135deg, #a33b3b 0%, #5c1d1d 100%);
  border-color: #2b0d0d;
}
</style>