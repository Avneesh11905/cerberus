import { useEffect, useState, useRef, createContext, useContext, type ReactNode } from 'react'
import { useAuthStore } from '../store/auth'
import { apiClient, API_URL } from '../lib/api-client'
import { fetchEventSource } from '@microsoft/fetch-event-source'

type AnalyticsContextType = {
  data: any
  status: 'connecting' | 'connected' | 'error'
}

const AnalyticsContext = createContext<AnalyticsContextType | null>(null)

export function AnalyticsProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<any>(null)
  const [status, setStatus] = useState<'connecting' | 'connected' | 'error'>('connecting')
  const abortControllerRef = useRef<AbortController | null>(null)
  const token = useAuthStore(state => state.accessToken)

  useEffect(() => {
    if (!token) return

    const connect = async () => {
      setStatus('connecting')
      abortControllerRef.current = new AbortController()

      try {
        await fetchEventSource(`${API_URL}/analytics/tenants/me/events/stream`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'text/event-stream',
          },
          openWhenHidden: true,
          signal: abortControllerRef.current.signal,
          onopen: async (response) => {
            if (response.ok && response.headers.get('content-type')?.includes('text/event-stream')) {
              setStatus('connected')
            } else {
              throw new Error(`Failed to connect: ${response.status}`)
            }
          },
          onmessage: (event) => {
            try {
              if (event.data) {
                const parsed = JSON.parse(event.data)
                setData(parsed)
              }
            } catch (e) {
              console.error('Failed to parse SSE data', e)
            }
          },
          onclose: () => {
            setStatus('error')
          },
          onerror: (err) => {
            if (err instanceof Error && err.name === 'AbortError') {
              return null; // Don't retry, just let it close
            }
            console.error('SSE Error:', err)
            setStatus('error')

            // If 401, trigger Axios interceptor to refresh the token, 
            // and stop fetchEventSource from retrying with the old token.
            if (err instanceof Error && err.message.includes('401')) {
              apiClient.get('/users/me').catch(() => {
                // If it fails, the interceptor handles logout
              })
              return null;
            }

            return 5000 // Retry after 5s for other errors
          }
        })
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          setStatus('error')
        }
      }
    }

    connect()

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [token])

  return (
    <AnalyticsContext.Provider value={{ data, status }}>
      {children}
    </AnalyticsContext.Provider>
  )
}

export function useAnalyticsStream() {
  const ctx = useContext(AnalyticsContext)
  if (!ctx) throw new Error('useAnalyticsStream must be used within AnalyticsProvider')
  return ctx
}
