import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const TOKEN_KEY = 'lydc_token'
const USER_KEY = 'lydc_user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const username = ref<string | null>(localStorage.getItem(USER_KEY))

  const isAuthenticated = computed(() => !!token.value)

  function setAuth(t: string, u: string) {
    token.value = t
    username.value = u
    localStorage.setItem(TOKEN_KEY, t)
    localStorage.setItem(USER_KEY, u)
  }

  function logout() {
    token.value = null
    username.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return { token, username, isAuthenticated, setAuth, logout }
})
