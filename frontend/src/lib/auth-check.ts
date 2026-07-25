import { refreshClient } from './api-client'
import { useAuthStore } from '../store/auth'

let sessionCheckPromise: Promise<string | null> | null = null;

export const checkInitialSession = (): Promise<string | null> => {
  if (typeof window === 'undefined') return Promise.resolve(null);
  if (sessionCheckPromise) return sessionCheckPromise;

  sessionCheckPromise = refreshClient.post('/auth/refresh')
    .then(res => {
      if (res.data.access_token) {
        if (res.data.user) {
          useAuthStore.getState().setAuth(res.data.access_token, res.data.csrf_token, res.data.user)
        } else {
          useAuthStore.getState().setAccessToken(res.data.access_token, res.data.csrf_token)
        }
        return res.data.access_token
      }
      return null
    })
    .catch(() => {
      useAuthStore.getState().setAccessToken(null, null)
      return null
    })


  return sessionCheckPromise;
}
