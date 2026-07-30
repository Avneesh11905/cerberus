import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'
import { Activity, Users, LogIn, AlertCircle } from 'lucide-react'
import { useAuthStore } from '../store/auth'
import { API_URL } from '../lib/api-client'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { useProject } from '../contexts/ProjectContext'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
} from 'recharts'

export const Route = createFileRoute(
  '/_protected/projects/$projectId/analytics',
)({
  component: AnalyticsTab,
})

interface MetricTotals {
  api_requests: number
  login_successes: number
  login_failures: number
  registrations: number
  active_users: number
}

interface DailyMetric {
  date: string
  api_requests: number
  login_successes: number
  login_failures: number
  registrations: number
  active_users: number
}

const TOOLTIP_STYLE = {
  contentStyle: {
    backgroundColor: '#FAEED1',
    border: '2px solid #3d405b',
    borderRadius: '8px',
    boxShadow: '4px 4px 0px rgba(61, 64, 91, 1)',
  },
  itemStyle: { fontWeight: 700 },
  labelStyle: { fontWeight: 900, color: '#3d405b', marginBottom: '8px' },
}

function AnalyticsTab() {
  const { projectId } = Route.useParams()
  const { project } = useProject()
  const accessToken = useAuthStore((state) => state.accessToken)

  const [timeSeries, setTimeSeries] = useState<DailyMetric[]>([])
  const [totals, setTotals] = useState<MetricTotals>({
    api_requests: 0,
    login_successes: 0,
    login_failures: 0,
    registrations: 0,
    active_users: 0,
  })

  // SSE for real-time metrics
  useEffect(() => {
    if (!accessToken) return

    let isMounted = true
    const controller = new AbortController()

    const connectStream = async () => {
      try {
        await fetchEventSource(
          `${API_URL}/analytics/projects/${projectId}/events/stream`,
          {
            method: 'GET',
            headers: { Authorization: `Bearer ${accessToken}` },
            signal: controller.signal,
            onmessage(ev) {
              if (ev.event === 'project_metrics_update' && ev.data) {
                const parsed = JSON.parse(ev.data)

                // Initial bulk payload with server-computed totals
                if (parsed.metrics && Array.isArray(parsed.metrics)) {
                  setTimeSeries(parsed.metrics)
                  if (parsed.totals) setTotals(parsed.totals)
                }

                // Live incremental event — bump both timeseries & totals
                if (parsed.event_type) {
                  setTotals((prev) => {
                    const next = { ...prev }
                    if (parsed.event_type === 'API_REQUEST')
                      next.api_requests += 1
                    else if (parsed.event_type === 'LOGIN_SUCCESS')
                      next.login_successes += 1
                    else if (parsed.event_type === 'LOGIN_FAILED')
                      next.login_failures += 1
                    else if (parsed.event_type === 'REGISTRATION')
                      next.registrations += 1
                    return next
                  })
                  setTimeSeries((prev) => {
                    if (prev.length === 0) return prev
                    const last = { ...prev[prev.length - 1] }
                    if (parsed.event_type === 'API_REQUEST')
                      last.api_requests += 1
                    else if (parsed.event_type === 'LOGIN_SUCCESS')
                      last.login_successes += 1
                    else if (parsed.event_type === 'LOGIN_FAILED')
                      last.login_failures += 1
                    else if (parsed.event_type === 'REGISTRATION')
                      last.registrations += 1
                    return [...prev.slice(0, -1), last]
                  })
                }
              }
            },
            onerror(err) {
              if (err instanceof Error && err.name === 'AbortError') return
              if ((err as any)?.name === 'AbortError') return

              console.error('SSE Error:', err)
              if (isMounted) setTimeout(connectStream, 5000)
            },
            onclose() {
              if (isMounted) setTimeout(connectStream, 5000)
            },
          },
        )
      } catch (err) {
        console.error('Failed to connect to SSE:', err)
      }
    }

    connectStream()

    return () => {
      isMounted = false
      controller.abort()
    }
  }, [projectId, accessToken])

  if (!project) return null

  return (
    <div className="flex flex-col gap-8 w-full animate-in fade-in slide-in-from-bottom-2 duration-300">
      {/* Stat Cards — use server-computed totals */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-sand">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <Activity className="w-5 h-5 text-terracotta" /> API Requests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">
              {totals.api_requests.toLocaleString()}
            </p>
            <p className="text-xs text-slate/50 font-medium mt-1">
              Last 30 days
            </p>
          </CardContent>
        </Card>

        <Card className="bg-sand">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <LogIn className="w-5 h-5 text-sage" /> Total Logins
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">
              {totals.login_successes.toLocaleString()}
            </p>
            <p className="text-xs text-slate/50 font-medium mt-1">
              Last 30 days
            </p>
          </CardContent>
        </Card>

        <Card className="bg-sand">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <Users className="w-5 h-5 text-ochre" /> Registrations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">
              {totals.registrations.toLocaleString()}
            </p>
            <p className="text-xs text-slate/50 font-medium mt-1">
              Last 30 days
            </p>
          </CardContent>
        </Card>

        <Card className="bg-sand">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <AlertCircle className="w-5 h-5 text-slate" /> Active Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">
              {totals.active_users.toLocaleString()}
            </p>
            <p className="text-xs text-slate/50 font-medium mt-1">
              Distinct, last 30 days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* API Traffic Area Chart */}
        <Card className="lg:col-span-2 bg-sand shadow-[4px_4px_0px_rgba(30,41,59,1)] border-2 border-slate">
          <CardHeader>
            <CardTitle>API Traffic</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            {timeSeries.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate/40 font-medium">
                No events yet — data will appear in real time.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={timeSeries}
                  margin={{ top: 5, right: 10, bottom: 5, left: -20 }}
                >
                  <defs>
                    <linearGradient
                      id="projColorRequests"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#E07A5F" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#E07A5F" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    stroke="#3d405b"
                    strokeDasharray="5 5"
                    opacity={0.1}
                  />
                  <XAxis
                    dataKey="date"
                    stroke="#3d405b"
                    tick={{ fill: '#3d405b', fontWeight: 600 }}
                    tickMargin={10}
                    fontSize={11}
                  />
                  <YAxis
                    stroke="#3d405b"
                    tick={{ fill: '#3d405b', fontWeight: 600 }}
                    fontSize={11}
                  />
                  <Tooltip {...TOOLTIP_STYLE} />
                  <Area
                    type="monotone"
                    dataKey="api_requests"
                    name="API Requests"
                    stroke="#E07A5F"
                    strokeWidth={3}
                    fill="url(#projColorRequests)"
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Auth Activity Bar Chart */}
        <Card className="bg-sand shadow-[4px_4px_0px_rgba(30,41,59,1)] border-2 border-slate">
          <CardHeader>
            <CardTitle>Auth Activity</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            {timeSeries.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate/40 font-medium text-sm text-center">
                No auth events yet.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={timeSeries}
                  margin={{ top: 5, right: 5, bottom: 5, left: -20 }}
                >
                  <CartesianGrid
                    stroke="#3d405b"
                    strokeDasharray="5 5"
                    opacity={0.1}
                  />
                  <XAxis
                    dataKey="date"
                    stroke="#3d405b"
                    fontSize={10}
                    tickLine={false}
                  />
                  <YAxis stroke="#3d405b" fontSize={10} tickLine={false} />
                  <Tooltip
                    {...TOOLTIP_STYLE}
                    cursor={{ fill: '#FAEED1', opacity: 0.5 }}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: '11px', fontWeight: 700 }}
                  />
                  <Bar
                    dataKey="login_successes"
                    name="Logins"
                    fill="#81B29A"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="registrations"
                    name="Registrations"
                    fill="#F2CC8F"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="login_failures"
                    name="Failures"
                    fill="#E07A5F"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
