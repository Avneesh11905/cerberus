import { useEffect, useRef } from 'react'
import { create } from 'zustand'
import { useAuthStore } from '../store/auth'
import { API_URL } from '../lib/api-client'
import { fetchEventSource } from '@microsoft/fetch-event-source'

export interface MetricTotals {
  api_requests: number
  login_successes: number
  login_failures: number
  registrations: number
  active_users: number
  projects_created?: number
}

export interface AnalyticsData {
  // Accurate period totals from the backend (COUNT DISTINCT for active_users)
  totals: MetricTotals
  // Daily timeseries for charts
  timeSeries: { date: string; api_requests: number; login_successes: number; login_failures: number; registrations: number; active_users: number }[]
  // System/superadmin specific
  platform_adoption?: any
  end_user_usage?: any
}

type AnalyticsState = {
  data: AnalyticsData | null
  status: 'disconnected' | 'connecting' | 'connected' | 'error'
  setData: (data: AnalyticsData) => void
  setStatus: (status: 'disconnected' | 'connecting' | 'connected' | 'error') => void
  processBulkData: (metrics: any[], totals?: MetricTotals) => void
  processLiveEvent: (event: any) => void
}

export const useAnalyticsStream = create<AnalyticsState>((set) => ({
  data: null,
  status: 'connecting',
  setData: (data) => set({ data }),
  setStatus: (status) => set({ status }),

  processBulkData: (metrics: any[], totals?: MetricTotals) =>
    set(() => {
      const timeSeries = metrics.map((row) => ({
        date: row.date ?? '',
        api_requests: row.api_requests ?? 0,
        login_successes: row.login_successes ?? 0,
        login_failures: row.login_failures ?? 0,
        registrations: row.registrations ?? 0,
        active_users: row.active_users ?? 0,
      }))

      return {
        data: {
          totals: totals ?? {
            api_requests: 0,
            login_successes: 0,
            login_failures: 0,
            registrations: 0,
            active_users: 0,
          },
          timeSeries,
        },
      }
    }),

  processLiveEvent: (event: any) =>
    set((state) => {
      if (!state.data) return state

      const et: string = event.event_type
      const newData = { ...state.data }
      const newTotals = { ...newData.totals }

      // ── Helper: bump a key on the last timeSeries entry (today's bar) ──────
      const bumpTimeSeries = (key: string, amount = 1) => {
        if (newData.timeSeries.length === 0) return
        const ts = [...newData.timeSeries]
        const last = { ...ts[ts.length - 1] }
        ;(last as any)[key] = ((last as any)[key] ?? 0) + amount
        ts[ts.length - 1] = last
        newData.timeSeries = ts
      }

      // ── Update totals + timeSeries together for every event type ──────────
      if (et === 'API_REQUEST') {
        newTotals.api_requests += 1
        bumpTimeSeries('api_requests')
      }
      if (et === 'LOGIN_SUCCESS') {
        newTotals.login_successes += 1
        bumpTimeSeries('login_successes')
      }
      if (et === 'LOGIN_FAILED') {
        newTotals.login_failures += 1
        bumpTimeSeries('login_failures')
      }
      if (et === 'REGISTRATION') {
        newTotals.registrations += 1
        bumpTimeSeries('registrations')
      }
      if (et === 'PROJECT_CREATED') {
        if (newTotals.projects_created !== undefined) newTotals.projects_created += 1
        bumpTimeSeries('projects_created')
      }
      if (et === 'EMAIL_SENT') {
        bumpTimeSeries('emails_sent')
      }
      if (et === 'EMAIL_FAILED') {
        bumpTimeSeries('emails_failed')
      }

      // ── Also update platform_adoption / end_user_usage for superadmin ─────
      if (newData.platform_adoption) {
        const pa = { ...newData.platform_adoption }
        if (et === 'API_REQUEST')    pa.api_requests    = (pa.api_requests    ?? 0) + 1
        if (et === 'LOGIN_SUCCESS')  pa.login_successes = (pa.login_successes ?? 0) + 1
        if (et === 'LOGIN_FAILED')   pa.login_failures  = (pa.login_failures  ?? 0) + 1
        if (et === 'REGISTRATION')   pa.registrations   = (pa.registrations   ?? 0) + 1
        if (et === 'TENANT_ONBOARDED') pa.total_tenants = (pa.total_tenants   ?? 0) + 1
        newData.platform_adoption = pa
      }
      if (newData.end_user_usage) {
        const eu = { ...newData.end_user_usage }
        if (et === 'PROJECT_CREATED') eu.total_projects = (eu.total_projects ?? 0) + 1
        if (et === 'REGISTRATION')    eu.registrations  = (eu.registrations  ?? 0) + 1
        newData.end_user_usage = eu
      }

      return { data: { ...newData, totals: newTotals } }
    }),
}))

export function AnalyticsProvider({
  children,
  projectId,
  scope = 'tenant',
}: {
  children: React.ReactNode
  projectId?: string
  scope?: 'tenant' | 'project' | 'system'
}) {
  const abortControllerRef = useRef<AbortController | null>(null)
  const token = useAuthStore((state) => state.accessToken)
  const setStatus = useAnalyticsStream((state) => state.setStatus)

  useEffect(() => {
    if (!token) return

    let isMounted = true

    const streamUrl =
      scope === 'project' && projectId
        ? `${API_URL}/analytics/projects/${projectId}/events/stream`
        : scope === 'system'
          ? `${API_URL}/analytics/system/events/stream`
          : `${API_URL}/analytics/tenants/me/events/stream`

    const connect = async () => {
      if (!isMounted) return

      setStatus('connecting')
      abortControllerRef.current = new AbortController()

      try {
        await fetchEventSource(streamUrl, {
          method: 'GET',
          headers: { Accept: 'text/event-stream' },
          fetch: async (input, init) => {
            let latestToken = useAuthStore.getState().accessToken
            const headers = { ...init?.headers, Authorization: `Bearer ${latestToken}` }
            let response = await fetch(input, { ...init, headers })

            if (response.status === 401) {
              try {
                const { refreshClient } = await import('../lib/api-client')
                const csrfToken = useAuthStore.getState().csrfToken
                const refreshRes = await refreshClient.post(
                  '/auth/refresh',
                  {},
                  { headers: csrfToken ? { 'X-CSRF': csrfToken } : undefined },
                )
                latestToken = refreshRes.data.access_token
                useAuthStore.getState().setAccessToken(latestToken, refreshRes.data.csrf_token)
                response = await fetch(input, { ...init, headers: { ...init?.headers, Authorization: `Bearer ${latestToken}` } })
              } catch {
                useAuthStore.getState().logout()
              }
            }
            return response
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
              if (!event.data) return
              const parsed = JSON.parse(event.data)

              // Initial bulk payload from the SSE endpoint
              if (parsed.metrics && Array.isArray(parsed.metrics)) {
                useAnalyticsStream.getState().processBulkData(parsed.metrics, parsed.totals)
              }

              // System analytics payload
              if (parsed.platform_adoption) {
                const current = useAnalyticsStream.getState().data
                useAnalyticsStream.getState().setData({
                  ...(current ?? { totals: { api_requests: 0, login_successes: 0, login_failures: 0, registrations: 0, active_users: 0 }, timeSeries: [] }),
                  timeSeries: parsed.metrics?.map((r: any) => ({
                    date: r.date ?? '',
                    api_requests: r.api_requests ?? 0,
                    login_successes: r.login_successes ?? 0,
                    login_failures: r.login_failures ?? 0,
                    registrations: r.registrations ?? 0,
                    active_users: r.active_users ?? 0,
                  })) ?? current?.timeSeries ?? [],
                  platform_adoption: parsed.platform_adoption,
                  end_user_usage: parsed.end_user_usage,
                  totals: {
                    api_requests: (parsed.platform_adoption?.api_requests ?? 0) + (parsed.end_user_usage?.api_requests ?? 0),
                    login_successes: (parsed.platform_adoption?.login_successes ?? 0) + (parsed.end_user_usage?.login_successes ?? 0),
                    login_failures: (parsed.platform_adoption?.login_failures ?? 0) + (parsed.end_user_usage?.login_failures ?? 0),
                    registrations: parsed.platform_adoption?.registrations ?? 0,
                    active_users: parsed.platform_adoption?.active_users ?? 0,
                  },
                })
              }

              // Live incremental event
              if (parsed.event_type) {
                useAnalyticsStream.getState().processLiveEvent(parsed)
              }
            } catch (e) {
              console.error('Failed to parse SSE data', e)
            }
          },
          onclose: () => { setStatus('error') },
          onerror: (err) => {
            if (err instanceof Error && err.name === 'AbortError') return null
            console.error('SSE Error:', err)
            setStatus('error')
            return 5000
          },
        })

        if (isMounted) setTimeout(connect, 5000)
      } catch (err: unknown) {
        if (err instanceof Error && err.name !== 'AbortError') {
          setStatus('error')
          if (isMounted) setTimeout(connect, 5000)
        }
      }
    }

    connect()

    return () => {
      isMounted = false
      abortControllerRef.current?.abort()
    }
  }, [token, scope, setStatus, projectId])

  return <>{children}</>
}
