import { createFileRoute, useRouter, Link } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { getProject } from '../api/projects'
import type { Project } from '../api/projects'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Settings, Activity, Users, LogIn, AlertCircle, ArrowLeft, TrendingDown } from 'lucide-react'
import { toast } from 'sonner'
import { useAuthStore } from '../store/auth'
import { API_URL } from '../lib/api-client'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
} from 'recharts'

export const Route = createFileRoute('/_protected/projects/$projectId/')({
  component: ProjectDashboardPage,
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

function ProjectDashboardPage() {
  const { projectId } = Route.useParams()
  const router = useRouter()
  const accessToken = useAuthStore((state) => state.accessToken)

  const [project, setProject] = useState<Project | null>(null)
  const [timeSeries, setTimeSeries] = useState<DailyMetric[]>([])
  const [totals, setTotals] = useState<MetricTotals>({ api_requests: 0, login_successes: 0, login_failures: 0, registrations: 0, active_users: 0 })
  const [loading, setLoading] = useState(true)

  // Load project info
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const projData = await getProject(projectId)
        setProject(projData)
      } catch {
        toast.error('Failed to load project dashboard')
        router.navigate({ to: '/projects' })
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [projectId, router])

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
                    if (parsed.event_type === 'API_REQUEST') next.api_requests += 1
                    else if (parsed.event_type === 'LOGIN_SUCCESS') next.login_successes += 1
                    else if (parsed.event_type === 'LOGIN_FAILED') next.login_failures += 1
                    else if (parsed.event_type === 'REGISTRATION') next.registrations += 1
                    return next
                  })
                  setTimeSeries((prev) => {
                    if (prev.length === 0) return prev
                    const last = { ...prev[prev.length - 1] }
                    if (parsed.event_type === 'API_REQUEST') last.api_requests += 1
                    else if (parsed.event_type === 'LOGIN_SUCCESS') last.login_successes += 1
                    else if (parsed.event_type === 'LOGIN_FAILED') last.login_failures += 1
                    else if (parsed.event_type === 'REGISTRATION') last.registrations += 1
                    return [...prev.slice(0, -1), last]
                  })
                }
              }
            },
            onerror(err) {
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <Activity className="w-8 h-8 animate-spin text-terracotta" />
      </div>
    )
  }

  if (!project) return null

  const errorRate = totals.api_requests > 0
    ? ((totals.login_failures / totals.api_requests) * 100).toFixed(1) + '%'
    : '0%'

  return (
    <div className="container max-w-7xl mx-auto px-4 py-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b-2 border-taupe/30 pb-6 mb-8">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="icon"
            className="border-2 border-slate w-10 h-10 rounded-xl"
            onClick={() => router.navigate({ to: '/projects' })}
          >
            <ArrowLeft className="w-5 h-5 text-slate" />
          </Button>
          <div>
            <h1 className="text-4xl font-display font-black tracking-tight text-slate">
              {project.name}
            </h1>
            <p className="text-slate/70 font-semibold mt-2">
              Project Analytics — Last 30 Days
            </p>
          </div>
        </div>
        <div className="flex gap-4">
          <Link to="/projects/$projectId/settings" params={{ projectId: project.id }}>
            <Button variant="primary" className="gap-2">
              <Settings className="w-4 h-4" /> Settings
            </Button>
          </Link>
        </div>
      </div>

      {/* Stat Cards — use server-computed totals */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-vanilla">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <Activity className="w-5 h-5 text-terracotta" /> API Requests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">{totals.api_requests.toLocaleString()}</p>
            <p className="text-xs text-slate/50 font-medium mt-1">Last 30 days</p>
          </CardContent>
        </Card>

        <Card className="bg-vanilla">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <LogIn className="w-5 h-5 text-sage" /> Total Logins
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">{totals.login_successes.toLocaleString()}</p>
            <p className="text-xs text-slate/50 font-medium mt-1">Last 30 days</p>
          </CardContent>
        </Card>

        <Card className="bg-vanilla">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <Users className="w-5 h-5 text-ochre" /> Registrations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">{totals.registrations.toLocaleString()}</p>
            <p className="text-xs text-slate/50 font-medium mt-1">Last 30 days</p>
          </CardContent>
        </Card>

        <Card className="bg-vanilla">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <AlertCircle className="w-5 h-5 text-slate" /> Active Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">{totals.active_users.toLocaleString()}</p>
            <p className="text-xs text-slate/50 font-medium mt-1">Distinct, last 30 days</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* API Traffic Area Chart */}
        <Card className="lg:col-span-2 bg-vanilla shadow-[4px_4px_0px_rgba(30,41,59,1)] border-2 border-slate">
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
                <AreaChart data={timeSeries} margin={{ top: 5, right: 10, bottom: 5, left: -20 }}>
                  <defs>
                    <linearGradient id="projColorRequests" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#E07A5F" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#E07A5F" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="#3d405b" strokeDasharray="5 5" opacity={0.1} />
                  <XAxis dataKey="date" stroke="#3d405b" tick={{ fill: '#3d405b', fontWeight: 600 }} tickMargin={10} fontSize={11} />
                  <YAxis stroke="#3d405b" tick={{ fill: '#3d405b', fontWeight: 600 }} fontSize={11} />
                  <Tooltip {...TOOLTIP_STYLE} />
                  <Area type="monotone" dataKey="api_requests" name="API Requests" stroke="#E07A5F" strokeWidth={3} fill="url(#projColorRequests)" dot={{ r: 3 }} activeDot={{ r: 5 }} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Auth Activity Bar Chart */}
        <Card className="bg-vanilla shadow-[4px_4px_0px_rgba(30,41,59,1)] border-2 border-slate">
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
                <BarChart data={timeSeries} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
                  <CartesianGrid stroke="#3d405b" strokeDasharray="5 5" opacity={0.1} />
                  <XAxis dataKey="date" stroke="#3d405b" fontSize={10} tickLine={false} />
                  <YAxis stroke="#3d405b" fontSize={10} tickLine={false} />
                  <Tooltip {...TOOLTIP_STYLE} cursor={{ fill: '#FAEED1', opacity: 0.5 }} />
                  <Legend wrapperStyle={{ fontSize: '11px', fontWeight: 700 }} />
                  <Bar dataKey="login_successes" name="Logins" fill="#81B29A" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="registrations" name="Registrations" fill="#F2CC8F" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="login_failures" name="Failures" fill="#E07A5F" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
