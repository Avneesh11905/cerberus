import { useEffect, useState, useRef, createContext, useContext, ReactNode } from 'react'
import { useAuthStore } from '../store/auth'
import { API_URL } from '../lib/api-client'
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
  
  useEffect(() => {
    const token = useAuthStore.getState().accessToken
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
            console.error('SSE Error:', err)
            setStatus('error')
            return 5000 // Retry after 5s
          }
        })
      } catch (err) {
        setStatus('error')
      }
    }

    connect()

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

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
