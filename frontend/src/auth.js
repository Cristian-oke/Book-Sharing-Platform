import { ref } from 'vue'

export const token = ref(localStorage.getItem('token') || '')
export const isAuthenticated = ref(!!token.value)

export function login(newToken) {
  token.value = newToken
  localStorage.setItem('token', newToken)
  isAuthenticated.value = true
}

export function logout() {
  token.value = ''
  localStorage.removeItem('token')
  isAuthenticated.value = false
}