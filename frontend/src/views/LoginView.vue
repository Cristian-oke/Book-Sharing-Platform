<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { login } from '../auth'

const router = useRouter()
const isLoginView = ref(true) //true-conectare false-inregistrare
const email = ref('')
const password = ref('')
const name = ref('')
const city = ref('')
const errorMessages = ref([])
const authSuccess = ref('')

const BASE_URL = 'http://localhost:5000/Book_Sharing' 

const handleAxiosError = (error) => {
  errorMessages.value = []
  
  if (error.response && error.response.data) {
    const data = error.response.data
    
    //cazul in care eroarea vine din validarea marshmallow
    if (data.errors) {
      
      Object.keys(data.errors).forEach(field => {
        const fieldErrors = data.errors[field]
        if (Array.isArray(fieldErrors)) {
          fieldErrors.forEach(msg => errorMessages.value.push(`${msg}`))
        } else {
          errorMessages.value.push(`${fieldErrors}`)
        }
      })
    } 
    //cazul in care eroarea este una de logica trimisa ca text
    else if (data.error) {
      errorMessages.value.push(data.error)
    } 
    // cazul in care backendul trimite un mesaj simplu generic
    else if (data.message) {
      errorMessages.value.push(data.message)
    }
  } else {
    //daca serverul este oprit complet sau e o eroare de retea
    errorMessages.value.push("Nu s-a putut stabili conexiunea cu serverul")
  }
}
const handleLogin = async () => {
  try {
    errorMessages.value = ''
    const response = await axios.post(`${BASE_URL}/auth/login`, {
      email: email.value,
      password: password.value
    })
    
    const jwtToken = response.data.access_token || response.data.token
    if (jwtToken) {
      login(jwtToken)
      router.push('/home')
    }
  } catch (error) {
    handleAxiosError(error)
  }
}

const handleRegister = async () => {
  try {
    errorMessages.value = ''
    authSuccess.value = ''
    await axios.post(`${BASE_URL}/auth/register`, {
      name: name.value,
      email: email.value,
      password: password.value,
      city: city.value
    })
    
    authSuccess.value = "Cont creat cu succes. Acum te poți conecta."
    isLoginView.value = true 
  } catch (error) {
    handleAxiosError(error)
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-box">
      <h2 style="text-align: center; margin-bottom: 20px; color: #2c3e50;">
        {{ isLoginView ? 'CONECTARE' : 'CREARE CONT NOU' }}</h2>
      
      <div v-if="errorMessages.length > 0" class="alert error">
        <ul class="error-list" style="list-style: none; padding: 0; margin: 0;">
            <li v-for="(err, index) in errorMessages" :key="index">⚠️ {{ err }}</li>
        </ul>
      </div>
      <div v-if="authSuccess" class="alert success">{{ authSuccess }}</div>

      <form @submit.prevent="isLoginView ? handleLogin() : handleRegister()">
        <div v-if="!isLoginView" class="form-group">
          <label>Nume complet:</label>
          <input v-model="name" type="text" required placeholder="Ex: Ioan Popescu" />
        </div>

        <div v-if="!isLoginView" class="form-group">
          <label>Oraș:</label>
          <input v-model="city" type="text" required placeholder="Ex: Bucuresti" />
        </div>

        <div class="form-group">
          <label>Email:</label>
          <input v-model="email" type="email" required placeholder="Ex: nume@email.com" />
        </div>

        <div class="form-group">
          <label>Parolă:</label>
          <input v-model="password" type="password" required placeholder="••••••••" />
        </div>

        <button type="submit" class="toggle-btn">
          {{ isLoginView ? 'Conectare' : 'Înregistrare' }}
        </button>
      </form>

      <div class="auth-toggle-zone">
        <hr />
        <p>{{ isLoginView ? 'Nu ai cont pe platformă?' : 'Ai deja un cont creat?' }}</p>
        <button class="toggle-btn" @click="isLoginView = !isLoginView; errorMessages = []" >
          {{ isLoginView ? 'Înregistrează-te' : 'Conectează-te' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}
.auth-box {
    
  width: 100%;
  max-width: 420px;
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  border: 1px solid #eee;
}
.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}
.form-group label {
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 0.9rem;
}
.form-group input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.submit-btn {
  width: 100%;
  padding: 12px;
  background: #42b983;
  color: white;
  border: none;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
}
.auth-toggle-zone {
  text-align: center;
  margin-top: 20px;
}
.auth-toggle-zone hr {
  border: 0;
  border-top: 1px solid #eee;
  margin-bottom: 15px;
}
.auth-toggle-zone p {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 5px;
}
.toggle-btn {
  background: none;
  border: 1px solid #35495e;
  color: #35495e;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  width: 100%;
}
.toggle-btn:hover {
  background: #35495e;
  color: white;
}
.alert { padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 0.9rem; font-weight: bold;}
.alert.error { background: #ffebee; color: #c62828; }
.alert.success { background: #e8f5e9; color: #2e7d32; }
</style>