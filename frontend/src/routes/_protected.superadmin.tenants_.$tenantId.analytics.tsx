import { createFileRoute, useRouter } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { getTenantAnalytics } from '../api/analytics'
import type { Metric } from '../api/analytics'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Activity, Users, LogIn, AlertCircle, ArrowLeft } from 'lucide-react'
import { toast } from 'sonner'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'

export const Route = createFileRoute(
  '/_protected/superadmin/tenants_/$tenantId/analytics',
)({
  component: SuperadminTenantAnalyticsPage,
})

function SuperadminTenantAnalyticsPage() {
  const { tenantId } = Route.useParams()
  const router = useRouter()

  const [metrics, setMetrics] = useState<Metric[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const metricsData = await getTenantAnalytics(tenantId)
        setMetrics(metricsData)
      } catch (err) {
        toast.error('Failed to load tenant analytics')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [tenantId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-100">
        <Activity className="w-8 h-8 animate-spin text-terracotta" />
      </div>
    )
  }

  // Calculate totals for the overview cards
  const totalRequests = metrics.reduce(
    (acc, curr) => acc + curr.api_requests,
    0,
  )
  const totalLogins = metrics.reduce(
    (acc, curr) => acc + curr.login_successes,
    0,
  )
  const totalRegistrations = metrics.reduce(
    (acc, curr) => acc + curr.registrations,
    0,
  )
  const activeUsers =
    metrics.length > 0 ? metrics[metrics.length - 1].active_users : 0

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-8 w-full">
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => router.navigate({ to: '/superadmin/tenants' })}
          className="font-bold border-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Tenants
        </Button>
      </div>
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b-2 border-slate/30 pb-6 mb-8">
        <div>
          <h1 className="text-4xl font-display font-black tracking-tight text-slate">
            Tenant Analytics
          </h1>
          <p className="text-slate/70 font-semibold mt-2 font-mono">
            ID: {tenantId}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <Activity className="w-5 h-5 text-terracotta" /> Total API
              Requests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">
              {totalRequests.toLocaleString()}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <LogIn className="w-5 h-5 text-sage" /> Total Logins
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">
              {totalLogins.toLocaleString()}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <Users className="w-5 h-5 text-ochre" /> Registrations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">
              {totalRegistrations.toLocaleString()}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-sand border-2 border-slate shadow-[4px_4px_0px_rgba(30,41,59,1)]">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2 text-slate/70">
              <AlertCircle className="w-5 h-5 text-slate" /> Active Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-black text-slate">
              {activeUsers.toLocaleString()}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-8">
        <Card className="bg-sand h-125 flex flex-col border-2 border-slate shadow-[8px_8px_0px_rgba(30,41,59,1)]">
          <CardHeader>
            <CardTitle>30-Day Activity</CardTitle>
          </CardHeader>
          <CardContent className="flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={metrics}
                margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
              >
                <Line
                  type="monotone"
                  dataKey="api_requests"
                  stroke="#E07A5F"
                  strokeWidth={3}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6 }}
                  name="API Requests"
                />
                <Line
                  type="monotone"
                  dataKey="login_successes"
                  stroke="#81B29A"
                  strokeWidth={3}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6 }}
                  name="Logins"
                />
                <Line
                  type="monotone"
                  dataKey="registrations"
                  stroke="#F2CC8F"
                  strokeWidth={3}
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6 }}
                  name="Registrations"
                />
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
                />
                <YAxis
                  stroke="#3d405b"
                  tick={{ fill: '#3d405b', fontWeight: 600 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FAEED1',
                    border: '2px solid #3d405b',
                    borderRadius: '8px',
                    boxShadow: '4px 4px 0px rgba(61, 64, 91, 1)',
                  }}
                  itemStyle={{ fontWeight: 700 }}
                  labelStyle={{
                    fontWeight: 900,
                    color: '#3d405b',
                    marginBottom: '8px',
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
