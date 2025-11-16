import axios, { type AxiosInstance } from 'axios'

export interface ApiConfig {
  baseURL: string
  timeout: number
}

export const createApiClient = (config: ApiConfig): AxiosInstance => {
  const client = axios.create({
    baseURL: config.baseURL,
    timeout: config.timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor for JWT tokens
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }

      // Add account context if available
      const currentAccount = localStorage.getItem('current_account')
      if (currentAccount) {
        config.headers['X-Account-ID'] = currentAccount
      }

      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Response interceptor for token refresh and error handling
  client.interceptors.response.use(
    (response) => {
      return response
    },
    (error) => {
      const originalRequest = error.config

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true

        // Try to refresh token
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          return axios
            .post(`${config.baseURL}/auth/token/refresh/`, {
              refresh: refreshToken,
            })
            .then((res) => {
              if (res.data.access) {
                localStorage.setItem('access_token', res.data.access)
                client.defaults.headers.common['Authorization'] = `Bearer ${res.data.access}`
                return client(originalRequest)
              }
            })
            .catch((refreshError) => {
              // Refresh failed, redirect to login
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              window.location.href = '/login'
              return Promise.reject(refreshError)
            })
        }
      }

      return Promise.reject(error)
    }
  )

  return client
}

export const apiConfig: ApiConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
}

export const apiClient = createApiClient(apiConfig)
