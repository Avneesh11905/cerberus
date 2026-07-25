import { useEffect, useRef } from 'react'
import { create } from 'zustand'
import { useAuthStore } from '../store/auth'
import { apiClient, API_URL } from '../lib/api-client'
import { fetchEventSource } from '@microsoft/fetch-event-source'

export interface AnalyticsData {
  totalRequests: number;
  activeUsers: number;
  errorRate: string;
  avgLatency: string;
  trends: {
    totalRequests: string;
    totalRequestsUp: boolean;
    activeUsers: string;
    activeUsersUp: boolean;
    errorRate: string;
    errorRateUp: boolean;
    avgLatency: string;
    avgLatencyUp: boolean;
  };
  timeSeries: { time: string; requests: number }[];
  endpoints: { name: string; calls: number }[];
}

type AnalyticsState = {
  data: AnalyticsData
  status: 'disconnected' | 'connecting' | 'connected' | 'error'
  setData: (data: AnalyticsData) => void
  setStatus: (status: 'disconnected' | 'connecting' | 'connected' | 'error') => void
}

const INITIAL_DATA: AnalyticsData = {
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
  const role = useAuthStore(state => state.user?.role)
  
  const setStatus = useAnalyticsStream(state => state.setStatus)
  const setData = useAnalyticsStream(state => state.setData)

  useEffect(() => {
    if (!token) return

    const streamUrl = role === 'SUPERADMIN' 
      ? `${API_URL}/analytics/system/events/stream`
      : `${API_URL}/analytics/tenants/me/events/stream`

    const connect = async () => {
      setStatus('connecting')
      abortControllerRef.current = new AbortController()

      try {
        await fetchEventSource(streamUrl, {
          method: 'GET',
          headers: {
            'Accept': 'text/event-stream',
          },
          fetch: async (input, init) => {
            let latestToken = useAuthStore.getState().accessToken;
            const headers = { ...init?.headers, 'Authorization': `Bearer ${latestToken}` };
            
            let response = await fetch(input, { ...init, headers });
            
            // If unauthorized, refresh the token and retry once
            if (response.status === 401) {
              try {
                const { refreshClient } = await import('../lib/api-client');
                const csrfToken = useAuthStore.getState().csrfToken;
                const refreshRes = await refreshClient.post('/auth/refresh', {}, {
                  headers: csrfToken ? { 'X-CSRF': csrfToken } : undefined
                });
                
                latestToken = refreshRes.data.access_token;
                useAuthStore.getState().setAccessToken(latestToken, refreshRes.data.csrf_token);
                
                const retryHeaders = { ...init?.headers, 'Authorization': `Bearer ${latestToken}` };
                response = await fetch(input, { ...init, headers: retryHeaders });
              } catch (err) {
                useAuthStore.getState().logout();
              }
            }
            return response;
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
            return 5000 
          }
        })
      } catch (err: unknown) {
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
  }, [token, role, setStatus, setData])

  return <>{children}</>
}
