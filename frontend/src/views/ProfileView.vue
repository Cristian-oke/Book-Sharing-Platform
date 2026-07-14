<script setup>
import { ref, onMounted ,computed} from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { isAuthenticated, token } from '../auth'

const router = useRouter()
const BASE_URL = 'http://localhost:5000'
const getAuthConfig = () => ({
  headers: { Authorization: `Bearer ${token.value}` }
})

</script>


<template>
  <div class="dashboard-container">
    
    <div v-if="!isAuthenticated" class="centered-auth-wrapper">
      <div class="simple-redirect-box">
        <h2>Nu ești autentificat</h2>
        <p>Trebuie să fii conectat pentru a avea acces la dashboard.</p>
        <button class="btn-simple-connect" @click="router.push('/login')">
          Conectează-te
        </button>
      </div>
    </div>
  </div>
  </template>

  <style scope>
  .dashboard-container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
  .centered-auth-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
}

.simple-redirect-box {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 35px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  border: 1px solid #eee;
  text-align: center;
}
.simple-redirect-box h2 { margin-bottom: 10px; color: #2c3e50; }
.simple-redirect-box p { color: #7f8c8d; font-size: 0.95rem; margin-bottom: 25px; line-height: 1.5; }
.btn-simple-connect { width: 100%; padding: 12px; background-color: #42b983; color: white; border: none; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 1rem; transition: background 0.2s; }
.btn-simple-connect:hover { background-color: #35495e; }
  </style>