import { ref, computed } from 'vue'
import router from './router'
import axios from 'axios'

export const token = ref(localStorage.getItem('token') || '')
export const isAuthenticated = computed(() => {
  if (!token.value) return false

  try {
    const base64Url = token.value.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const payload = JSON.parse(atob(base64))
    
    const isExpired = payload.exp * 1000 <= Date.now()

    if (isExpired) {
      localStorage.removeItem('token')
      token.value = ''
      return false
    }

    return true
  } catch (e) {
    localStorage.removeItem('token')
    token.value = ''
    return false
  }
})

export function login(newToken) {
  token.value = newToken
  localStorage.setItem('token', newToken)
  isHandled401 = false
}

export function logout() {
  token.value = ''
  localStorage.removeItem('token')
}

let isHandled401 = false

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      //executare o singura data pana la urmatoarea autentificare
      if (!isHandled401) {
        isHandled401 = true //blocheaza orice alt apel paralel
        logout()
        router.push('/login').then(() => {
          setTimeout(() => {
            alert("Sesiunea ta a expirat. Te rugăm să te autentifici din nou.")
          }, 100)
        })
      }
    }
    return Promise.reject(error)
  }
)