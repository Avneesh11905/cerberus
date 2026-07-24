import { useEffect, useRef } from 'react'
import { create } from 'zustand'
import { useAuthStore } from '../store/auth'
import { apiClient, API_URL } from '../lib/api-client'
import { fetchEventSource } from '@microsoft/fetch-event-source'

type AnalyticsState = {
  data: any
  status: 'connecting' | 'connected' | 'error'
  setData: (data: any) => void
  setStatus: (status: 'connecting' | 'connected' | 'error') => void
}

const INITIAL_DATA = {
  totalRequests: 0,
  activeUsers: 0,
  errorRate: '0%',
  avgLatency: '0ms',
  trends: {
    totalRequests: '0%', totalRequestsUp: true,
    activeUsers: '0%', activeUsersUp: true,
    errorRate: '0%', errorRateUp: false,
    avgLatency: '0ms', avgLatencyUp: false
  },
  timeSeries: [
    { time: '00:00', requests: 0 },
    { time: '04:00', requests: 0 },
    { time: '08:00', requests: 0 },
    { time: '12:00', requests: 0 },
    { time: '16:00', requests: 0 },
    { time: '20:00', requests: 0 },
  ],
  endpoints: []
}

export const useAnalyticsStream = create<AnalyticsState>((set) => ({
  data: INITIAL_DATA,
  status: 'connecting',
  setData: (data) => set({ data }),
  setStatus: (status) => set({ status }),
}))

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const abortControllerRef = useRef<AbortController | null>(null)
  const token = useAuthStore(state => state.accessToken)
  
  const setStatus = useAnalyticsStream(state => state.setStatus)
  const setData = useAnalyticsStream(state => state.setData)

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
              return null;
            }
            console.error('SSE Error:', err)
            setStatus('error')

            if (err instanceof Error && err.message.includes('401')) {
              apiClient.get('/users/me').catch(() => {})
              return null;
            }

            return 5000 
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
  }, [token, setStatus, setData])

  return <>{children}</>
}
