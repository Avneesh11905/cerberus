import { refreshClient } from './api-client'
import { useAuthStore } from '../store/auth'

let sessionCheckPromise: Promise<string | null> | null = null

export const checkInitialSession = (): Promise<string | null> => {
  if (typeof window === 'undefined') return Promise.resolve(null)

  // Return the in-flight promise to deduplicate concurrent calls during
  // the same navigation event (e.g. multiple beforeLoad guards firing at once).
  // But do NOT cache the resolved value — every fresh page load should
  // attempt a refresh so the access token stays current.
  if (sessionCheckPromise) return sessionCheckPromise

  sessionCheckPromise = refreshClient
    .post('/auth/refresh')
    .then((res) => {
      if (res.data.access_token) {
        if (res.data.user) {
          useAuthStore
            .getState()
            .setAuth(res.data.access_token, res.data.csrf_token, res.data.user)
        } else {
          useAuthStore
            .getState()
            .setAccessToken(res.data.access_token, res.data.csrf_token)
        }
        return res.data.access_token as string
      }
      return null
    })
    .catch((err) => {
      // Only clear auth state on an explicit 401 (invalid/expired refresh token).
      // Do NOT logout on network errors or 5xx — the user might just be offline
      // and we should not destroy their cached session.
      const status = err?.response?.status
      if (status === 401) {
        useAuthStore.getState().logout()
      }
      return null
    })
    .finally(() => {
      // Always reset so the NEXT navigation triggers a real refresh request.
      sessionCheckPromise = null
    })

  return sessionCheckPromise
}
