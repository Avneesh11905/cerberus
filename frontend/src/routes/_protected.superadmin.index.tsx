import { createFileRoute } from '@tanstack/react-router'
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import {
  Users,
  FolderKanban,
  Activity,
  Globe,
  LogIn,
  ShieldAlert,
  TrendingUp,
} from 'lucide-react'
import { useAnalyticsStream } from '../hooks/useAnalyticsStream'

export const Route = createFileRoute('/_protected/superadmin/')({
  component: SuperadminAnalyticsPage,
})

const TOOLTIP_STYLE = {
  contentStyle: {
    backgroundColor: '#FAEED1',
    border: '2px solid #3d405b',
    borderRadius: '8px',
    color: '#3d405b',
    fontWeight: 'bold',
    boxShadow: '4px 4px 0px rgba(61, 64, 91, 1)',
  },
  itemStyle: { color: '#3d405b' },
  labelStyle: { color: '#3d405b', fontWeight: 900, marginBottom: '4px' },
}

function StatCard({
  title,
  value,
  sub,
  icon: Icon,
  accent = '#3d405b',
}: {
  title: string
  value: string | number
  sub?: string
  icon: any
  accent?: string
}) {
  return (
    <Card className="bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-bold text-slate/60 uppercase tracking-wider">
          {title}
        </CardTitle>
        <Icon className="w-4 h-4" style={{ color: accent }} />
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-display font-bold text-slate">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </div>
        {sub && <p className="text-xs font-medium text-slate/50 mt-1">{sub}</p>}
      </CardContent>
    </Card>
  )
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-base font-bold text-slate/50 uppercase tracking-widest mt-2">
      {children}
    </h2>
  )
}

function EmptyChart({ loading }: { loading: boolean }) {
  return (
    <div className="h-full flex items-center justify-center text-slate/30 font-medium text-sm">
      {loading
        ? <div className="animate-spin h-6 w-6 border-3 border-ochre border-t-transparent rounded-full" />
        : 'No data yet — will appear in real time.'}
    </div>
  )
}

function SuperadminAnalyticsPage() {
  const data = useAnalyticsStream((state) => state.data)
  const status = useAnalyticsStream((state) => state.status)
  const isLoading = !data && status === 'connecting'

  const pa = data?.platform_adoption   // PlatformAdoptionMetrics
  const eu = data?.end_user_usage      // EndUserUsageMetrics
  const ts = data?.timeSeries ?? []    // daily timeseries

  // platform_adoption now covers ALL platform events (tenant + project-scoped).
  // end_user_usage covers only project-scoped events (subset of the above).
  // To avoid double-counting, use pa for global totals on the stat cards.
  const totalApiRequests = pa?.api_requests ?? 0
  const totalLogins      = pa?.login_successes ?? 0
  const totalFailures    = pa?.login_failures ?? 0
  const totalAttempts    = totalLogins + totalFailures
  const errorRate = totalAttempts > 0
    ? ((totalFailures / totalAttempts) * 100).toFixed(1) + '%'
    : '0.0%'

  // Timeseries keys available from backend: date, api_requests, active_users,
  // login_successes, login_failures, registrations, emails_sent, emails_failed,
  // projects_created

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-8 w-full">

      {/* ── Header ────────────────────────────────────────────────────── */}
      <div>
        <h1 className="text-2xl font-display font-bold text-slate">System Analytics</h1>
        <p className="text-sm font-medium text-slate/50 mt-1">
          Platform-wide live data · all figures from real events
        </p>
      </div>

      {/* ── Section 1: Platform (Tenant) stats ─────────────────────── */}
      <SectionTitle>Platform Adoption</SectionTitle>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard
          title="Tenants"
          value={pa?.total_tenants ?? 0}
          sub="All time"
          icon={Globe}
          accent="#E07A5F"
        />
        <StatCard
          title="Projects"
          value={eu?.total_projects ?? 0}
          sub="All time"
          icon={FolderKanban}
          accent="#81B29A"
        />
        <StatCard
          title="Total Users"
          value={pa?.registrations ?? 0}
          sub="Registered all time"
          icon={Users}
          accent="#F2CC8F"
        />
        <StatCard
          title="Active Users"
          value={pa?.active_users ?? 0}
          sub="Distinct, last 30d"
          icon={TrendingUp}
          accent="#3d405b"
        />
        <StatCard
          title="Total Logins"
          value={totalLogins}
          sub="Tenant + project, all time"
          icon={LogIn}
          accent="#81B29A"
        />
        <StatCard
          title="Error Rate"
          value={errorRate}
          sub="Login failures / requests"
          icon={ShieldAlert}
          accent="#E07A5F"
        />
      </div>

      {/* ── Section 2: Usage stats ──────────────────────────────────── */}
      <SectionTitle>End-User Activity</SectionTitle>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="API Requests"
          value={totalApiRequests}
          sub="All projects, all time"
          icon={Activity}
          accent="#E07A5F"
        />
        <StatCard
          title="Login Failures"
          value={totalFailures}
          sub="All projects, all time"
          icon={ShieldAlert}
          accent="#E07A5F"
        />
        <StatCard
          title="Project Registrations"
          value={eu?.registrations ?? 0}
          sub="Users in projects"
          icon={Users}
          accent="#F2CC8F"
        />
        <StatCard
          title="Project API Hits"
          value={eu?.api_requests ?? 0}
          sub="From live_project_metrics"
          icon={Activity}
          accent="#3d405b"
        />
      </div>

      {/* ── Section 3: Charts ──────────────────────────────────────── */}
      <SectionTitle>Trends — Last 30 Days</SectionTitle>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* API Traffic */}
        <Card className="lg:col-span-2 bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <CardHeader>
            <CardTitle className="text-base">API Traffic</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            {ts.length === 0 ? <EmptyChart loading={isLoading} /> : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={ts} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
                  <defs>
                    <linearGradient id="gApi" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#E07A5F" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#E07A5F" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3d405b" opacity={0.1} vertical={false} />
                  <XAxis dataKey="date" fontSize={10} tickLine={false} axisLine={false} stroke="#3d405b" />
                  <YAxis fontSize={10} tickLine={false} axisLine={false} stroke="#3d405b" />
                  <Tooltip {...TOOLTIP_STYLE} />
                  <Area type="monotone" dataKey="api_requests" name="API Requests" stroke="#E07A5F" strokeWidth={2.5} fill="url(#gApi)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Auth Activity */}
        <Card className="bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <CardHeader>
            <CardTitle className="text-base">Auth Activity</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            {ts.length === 0 ? <EmptyChart loading={isLoading} /> : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={ts} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3d405b" opacity={0.1} vertical={false} />
                  <XAxis dataKey="date" fontSize={9} tickLine={false} axisLine={false} stroke="#3d405b" />
                  <YAxis fontSize={9} tickLine={false} axisLine={false} stroke="#3d405b" />
                  <Tooltip {...TOOLTIP_STYLE} cursor={{ fill: '#FAEED1', opacity: 0.4 }} />
                  <Legend wrapperStyle={{ fontSize: '10px', fontWeight: 700 }} />
                  <Bar dataKey="login_successes" name="Logins" fill="#81B29A" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="registrations" name="Registrations" fill="#F2CC8F" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="login_failures" name="Failures" fill="#E07A5F" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Emails */}
        <Card className="bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <CardHeader>
            <CardTitle className="text-base">Emails Sent</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            {ts.length === 0 ? <EmptyChart loading={isLoading} /> : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={ts} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
                  <defs>
                    <linearGradient id="gEmail" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#81B29A" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#81B29A" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gEmailFail" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#E07A5F" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#E07A5F" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3d405b" opacity={0.1} vertical={false} />
                  <XAxis dataKey="date" fontSize={10} tickLine={false} axisLine={false} stroke="#3d405b" />
                  <YAxis fontSize={10} tickLine={false} axisLine={false} stroke="#3d405b" />
                  <Tooltip {...TOOLTIP_STYLE} />
                  <Legend wrapperStyle={{ fontSize: '10px', fontWeight: 700 }} />
                  <Area type="monotone" dataKey="emails_sent" name="Sent" stroke="#81B29A" strokeWidth={2} fill="url(#gEmail)" />
                  <Area type="monotone" dataKey="emails_failed" name="Failed" stroke="#E07A5F" strokeWidth={2} fill="url(#gEmailFail)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Projects Created + Active Users */}
        <Card className="lg:col-span-2 bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <CardHeader>
            <CardTitle className="text-base">Growth — Projects Created & Active Users</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            {ts.length === 0 ? <EmptyChart loading={isLoading} /> : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={ts} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
                  <defs>
                    <linearGradient id="gProj" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#F2CC8F" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#F2CC8F" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gActive" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3d405b" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#3d405b" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3d405b" opacity={0.1} vertical={false} />
                  <XAxis dataKey="date" fontSize={10} tickLine={false} axisLine={false} stroke="#3d405b" />
                  <YAxis fontSize={10} tickLine={false} axisLine={false} stroke="#3d405b" />
                  <Tooltip {...TOOLTIP_STYLE} />
                  <Legend wrapperStyle={{ fontSize: '10px', fontWeight: 700 }} />
                  <Area type="monotone" dataKey="projects_created" name="Projects Created" stroke="#F2CC8F" strokeWidth={2} fill="url(#gProj)" />
                  <Area type="monotone" dataKey="active_users" name="Active Users" stroke="#3d405b" strokeWidth={2} fill="url(#gActive)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

      </div>
    </div>
  )
}
