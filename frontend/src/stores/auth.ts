import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, TokenResponse, LoginCredentials, RegisterData } from '@/types/api'
import { apiClient } from '@/services/api/config'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  // Actions
  const initializeAuth = () => {
    const token = localStorage.getItem('access_token')
    const refresh = localStorage.getItem('refresh_token')
    const savedUser = localStorage.getItem('user')

    if (token) {
      accessToken.value = token
    }
    if (refresh) {
      refreshToken.value = refresh
    }
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (e) {
        console.error('Failed to parse saved user:', e)
        localStorage.removeItem('user')
      }
    }
  }

  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post<TokenResponse>('/auth/token/', credentials)
      const data = response.data

      accessToken.value = data.access
      refreshToken.value = data.refresh
      user.value = data.user

      // Persist to localStorage
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))

      return data.user
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = async (data: RegisterData) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post<User>('/register/', data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    accessToken.value = null
    refreshToken.value = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('current_account')
  }

  const updateUser = (updatedUser: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...updatedUser }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await apiClient.post('/auth/token/refresh/', {
        refresh: refreshToken.value,
      })

      const data = response.data
      accessToken.value = data.access
      localStorage.setItem('access_token', data.access)

      return data.access
    } catch (err) {
      logout() // Force logout if refresh fails
      throw err
    }
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,

    // Getters
    isAuthenticated,

    // Actions
    initializeAuth,
    login,
    register,
    logout,
    updateUser,
    refreshAccessToken,
  }
})
