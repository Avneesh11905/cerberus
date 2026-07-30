import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../store/auth'
import type { User } from '../store/auth'

export function extractErrorMessage(
  error: unknown,
  fallback = 'An error occurred',
): string {
  if (!error) return fallback

  if (axios.isAxiosError(error)) {
    const data = error.response?.data
    const detail = data?.detail

    if (Array.isArray(detail) && detail.length > 0 && detail[0].msg)
      return String(detail[0].msg)
    if (typeof detail === 'string') return detail
    if (typeof detail === 'object' && detail !== null && detail.msg)
      return String(detail.msg)

    if (Array.isArray(data) && data.length > 0 && data[0].msg)
      return String(data[0].msg)
    if (typeof data === 'object' && data !== null && data.msg)
      return String(data.msg)
  }

  if (error instanceof Error) return error.message
  if (typeof error === 'string') return error

  return fallback
}

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/v1'

export const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Crucial for sending the HTTP-only refresh cookie
  xsrfCookieName: 'csrf_token', // Axios will automatically read this cookie
  xsrfHeaderName: 'X-CSRF', // and append it to this header for unsafe methods
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken, csrfToken } = useAuthStore.getState()
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    if (csrfToken && config.headers) {
      config.headers['X-CSRF'] = csrfToken
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

export const refreshClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  xsrfCookieName: 'csrf_token',
  xsrfHeaderName: 'X-CSRF',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const refreshToken = async (): Promise<string> => {
  if (isRefreshing) {
    return new Promise<string>((resolve, reject) => {
      failedQueue.push({ resolve: resolve as any, reject })
    })
  }

  isRefreshing = true

  try {
    const csrfToken = useAuthStore.getState().csrfToken
    const { data } = await refreshClient.post<{
      access_token: string
      csrf_token?: string
      user?: User
    }>(
      '/auth/refresh',
      {},
      {
        headers: csrfToken ? { 'X-CSRF': csrfToken } : undefined,
      },
    )

    const newAccessToken = data.access_token
    const newCsrfToken = data?.csrf_token
    if (data.user) {
      useAuthStore
        .getState()
        .setAuth(newAccessToken, newCsrfToken || '', data.user)
    } else {
      useAuthStore.getState().setAccessToken(newAccessToken, newCsrfToken)
    }

    processQueue(null, newAccessToken)
    return newAccessToken
  } catch (refreshError) {
    processQueue(refreshError as Error, null)
    useAuthStore.getState().logout()
    return Promise.reject(refreshError)
  } finally {
    isRefreshing = false
  }
}

apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }
    const isAuthRoute =
      originalRequest.url?.includes('/auth/login') ||
      originalRequest.url?.includes('/auth/verify-email') ||
      originalRequest.url?.includes('/auth/refresh') ||
      originalRequest.url?.includes('/auth/password')

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isAuthRoute
    ) {
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = 'Bearer ' + token
            return apiClient(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      try {
        const newAccessToken = await refreshToken()
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        const newCsrfToken = useAuthStore.getState().csrfToken
        if (newCsrfToken) {
          originalRequest.headers['X-CSRF'] = newCsrfToken
        }
        return apiClient(originalRequest)
      } catch (refreshError) {
        return Promise.reject(refreshError)
      }
    }

    if (
      error.response?.status === 403 &&
      !originalRequest.url?.includes('/users/me')
    ) {
      const accessToken = useAuthStore.getState().accessToken
      if (accessToken) {
        // Use a fresh axios instance to avoid interceptor loops
        axios
          .get(`${API_URL}/users/me`, {
            headers: { Authorization: `Bearer ${accessToken}` },
          })
          .then(({ data }) => {
            const currentUser = useAuthStore.getState().user
            if (currentUser && currentUser.role !== data.role) {
              useAuthStore.getState().setUser(data)
              window.location.href = '/dashboard'
            }
          })
          .catch(() => {})
      }
    }

    return Promise.reject(error)
  },
)
