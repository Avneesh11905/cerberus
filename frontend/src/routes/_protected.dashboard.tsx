import React from 'react'
import { createFileRoute, useNavigate, useRouter } from '@tanstack/react-router'
import { useAnalyticsStream } from '../hooks/useAnalyticsStream'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
} from 'recharts'
import { Activity, Users, ShieldAlert, LogIn, FolderKanban, ArrowLeft } from 'lucide-react'
import { Button } from '../components/ui/button'

export const Route = createFileRoute('/_protected/dashboard')({
  component: DashboardPage,
})

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ElementType
  subtitle?: string
}

function StatCard({ title, value, icon: Icon, subtitle }: StatCardProps) {
  return (
    <div className="bg-sand rounded-xl border-2 border-slate p-6 shadow-[4px_4px_0px_rgba(30,41,59,1)] flex flex-col">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-slate font-bold">{title}</h3>
        <div className="p-2 bg-taupe/10 rounded-lg border-2 border-slate">
          <Icon className="w-5 h-5 text-slate" />
        </div>
      </div>
      <div className="text-3xl font-display font-bold text-slate mb-1">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      {subtitle && <p className="text-sm font-medium text-slate/50">{subtitle}</p>}
    </div>
  )
}

function DashboardPage() {
  const data = useAnalyticsStream((state) => state.data)
  const status = useAnalyticsStream((state) => state.status)
  const navigate = useNavigate()
  const router = useRouter()

  if (!data && status === 'connecting')
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-4 h-full">
        <div className="animate-spin h-10 w-10 border-4 border-slate border-t-transparent rounded-full" />
      </div>
    )

  const totals = data?.totals
  const timeSeries = data?.timeSeries ?? []
  const errorRate = totals && totals.api_requests > 0
    ? ((totals.login_failures / totals.api_requests) * 100).toFixed(1) + '%'
    : '0%'

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-8 w-full">
      <div className="flex justify-between items-end">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="icon"
            className="border-2 border-slate w-10 h-10 rounded-xl"
            onClick={() => router.navigate({ to: '/' })}
          >
            <ArrowLeft className="w-5 h-5 text-slate" />
          </Button>
          <div>
            <h1 className="text-3xl font-display font-bold text-slate mb-2">
              Dashboard Overview
            </h1>
            <p className="text-slate/70 font-medium">
              Real-time metrics for your infrastructure — last 30 days.
            </p>
          </div>
        </div>
        <Button
          variant="primary"
          onClick={() => navigate({ to: '/projects' })}
          className="hidden sm:flex items-center gap-2"
        >
          <FolderKanban className="w-4 h-4" />
          View Projects
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total API Requests"
          value={totals?.api_requests ?? 0}
          icon={Activity}
          subtitle="Last 30 days"
        />
        <StatCard
          title="Active Users"
          value={totals?.active_users ?? 0}
          icon={Users}
          subtitle="Distinct users, last 30d"
        />
        <StatCard
          title="Total Logins"
          value={totals?.login_successes ?? 0}
          icon={LogIn}
          subtitle="Last 30 days"
        />
        <StatCard
          title="Error Rate"
          value={errorRate}
          icon={ShieldAlert}
          subtitle="Login failures / requests"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart — API Requests over time */}
        <div className="lg:col-span-2 bg-sand rounded-xl border-2 border-slate p-6 shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <h2 className="text-xl font-bold text-slate mb-6">API Traffic — Last 30 Days</h2>
          {timeSeries.length === 0 ? (
            <div className="h-80 flex items-center justify-center text-slate/40 font-medium">
              No data yet — events will appear here in real time.
            </div>
          ) : (
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={timeSeries}
                  margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#E07A5F" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#E07A5F" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3d405b" vertical={false} />
                  <XAxis dataKey="date" stroke="#3d405b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#3d405b" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#FAEED1',
                      border: '2px solid #3d405b',
                      borderRadius: '8px',
                      color: '#3d405b',
                      fontWeight: 'bold',
                      boxShadow: '4px 4px 0px rgba(61, 64, 91, 1)',
                    }}
                    itemStyle={{ color: '#3d405b' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="api_requests"
                    name="API Requests"
                    stroke="#E07A5F"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorRequests)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Side Chart — Logins vs Registrations */}
        <div className="bg-sand rounded-xl border-2 border-slate p-6 shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <h2 className="text-xl font-bold text-slate mb-6">Auth Activity</h2>
          {timeSeries.length === 0 ? (
            <div className="h-80 flex items-center justify-center text-slate/40 font-medium text-center text-sm">
              No auth events yet.
            </div>
          ) : (
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={timeSeries}
                  margin={{ top: 0, right: 0, left: -20, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#3d405b" vertical={false} />
                  <XAxis dataKey="date" stroke="#3d405b" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#3d405b" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip
                    cursor={{ fill: '#FAEED1', opacity: 0.5 }}
                    contentStyle={{
                      backgroundColor: '#FAEED1',
                      border: '2px solid #3d405b',
                      borderRadius: '8px',
                      color: '#3d405b',
                      fontWeight: 'bold',
                      boxShadow: '4px 4px 0px rgba(61, 64, 91, 1)',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', fontWeight: 700 }} />
                  <Bar dataKey="login_successes" name="Logins" fill="#81B29A" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="registrations" name="Registrations" fill="#F2CC8F" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="login_failures" name="Failures" fill="#E07A5F" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
