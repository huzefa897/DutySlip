import axios from 'axios'
import { accessToken, refreshToken, setTokens, clearAuth } from '../store/auth'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost/api'

const api = axios.create({ baseURL: BASE_URL })

// ── Request: attach Bearer token ──────────────────────────────
api.interceptors.request.use(config => {
  const token = accessToken.value
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response: silent 401 refresh ─────────────────────────────
let isRefreshing = false
let failedQueue  = []

function processQueue(error, token = null) {
  failedQueue.forEach(p => error ? p.reject(error) : p.resolve(token))
  failedQueue = []
}

api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      if (!refreshToken.value) {
        clearAuth()
        window.location.href = '/login'
        return Promise.reject(err)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          original.headers.Authorization = `Bearer ${token}`
          return api(original)
        })
      }

      original._retry = true
      isRefreshing = true

      try {
        const res = await axios.post(`${BASE_URL}/auth/refresh/`, {
          refresh: refreshToken.value,
        })
        const newAccess  = res.data.access
        const newRefresh = res.data.refresh   // rotation enabled
        setTokens(newAccess, newRefresh)
        processQueue(null, newAccess)
        original.headers.Authorization = `Bearer ${newAccess}`
        return api(original)
      } catch (refreshErr) {
        processQueue(refreshErr, null)
        clearAuth()
        window.location.href = '/login'
        return Promise.reject(refreshErr)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(err)
  }
)

export default api
