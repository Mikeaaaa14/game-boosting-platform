/**
 * Axios HTTP client configuration with JWT interceptor.
 * Automatically injects authentication token into requests.
 */

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const rawApiBaseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const apiBaseURL = rawApiBaseURL.endsWith('/')
  ? rawApiBaseURL.slice(0, -1)
  : rawApiBaseURL

function apiPath(path) {
  return `${apiBaseURL}${path}`
}

// Create axios instance with base configuration
const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - inject JWT token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.accessToken
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors and token refresh
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // Try to refresh token
      if (authStore.refreshToken) {
        try {
          const response = await axios.post(apiPath('/auth/refresh'), {
            refresh_token: authStore.refreshToken,
          })
          
          const { access_token, refresh_token } = response.data
          authStore.setTokens(access_token, refresh_token)
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, logout user
          authStore.logout()
          router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, redirect to login
        authStore.logout()
        router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
      }
    }
    
    // Handle other errors
    const errorMessage = error.response?.data?.detail || error.message || '请求失败'
    
    return Promise.reject({
      status: error.response?.status,
      message: errorMessage,
      errors: error.response?.data?.errors,
      original: error,
    })
  }
)

export default api
