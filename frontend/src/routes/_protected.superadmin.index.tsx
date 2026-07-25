import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { getSystemAnalytics } from '../api/superadmin'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Users, FolderKanban, Activity, Globe } from 'lucide-react'
import { Skeleton } from '../components/ui/skeleton'

export const Route = createFileRoute('/_protected/superadmin/')({
  component: SuperadminAnalyticsPage,
})

function StatCard({ title, value, subValue, icon: Icon, loading }: { title: string, value: string | number, subValue?: string, icon: any, loading: boolean }) {
  return (
    <Card className="bg-vanilla border-ochre/30 shadow-[4px_4px_0px_var(--ochre)]">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-bold text-slate/70 uppercase tracking-wider">{title}</CardTitle>
        <Icon className="w-5 h-5 text-ochre" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-20 mb-1 bg-ochre/20" />
        ) : (
          <div className="text-3xl font-display font-bold text-slate">{value}</div>
        )}
        {loading ? (
          <Skeleton className="h-4 w-32 bg-ochre/10 mt-2" />
        ) : subValue && (
          <p className="text-sm font-semibold text-slate/60 mt-1">{subValue}</p>
        )}
      </CardContent>
    </Card>
  )
}

function SuperadminAnalyticsPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['superadmin-analytics'],
    queryFn: getSystemAnalytics,
    refetchInterval: 30000, // Refresh every 30s
  })

  return (
    <div className="space-y-6 pt-4">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-xl font-bold text-slate">Global Overview</h2>
          <p className="text-sm font-semibold text-slate/60 mt-1">Platform-wide statistics and metrics.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total Tenants" 
          value={analytics?.total_tenants || 0} 
          subValue={`${analytics?.active_tenants || 0} active accounts`}
          icon={Globe} 
          loading={isLoading} 
        />
        <StatCard 
          title="Total Projects" 
          value={analytics?.total_projects || 0} 
          subValue={`${analytics?.active_projects || 0} active projects`}
          icon={FolderKanban} 
          loading={isLoading} 
        />
        <StatCard 
          title="Total End Users" 
          value={analytics?.total_users || 0} 
          subValue={`${analytics?.active_users || 0} active users`}
          icon={Users} 
          loading={isLoading} 
        />
        <StatCard 
          title="System Status" 
          value="Healthy" 
          subValue={analytics?.last_updated ? `Last updated: ${new Date(analytics.last_updated).toLocaleTimeString()}` : 'Live'}
          icon={Activity} 
          loading={isLoading} 
        />
      </div>

      <div className="mt-8 p-12 bg-ochre/5 border-2 border-dashed border-ochre/20 rounded-xl flex flex-col items-center justify-center text-center">
        <Activity className="w-12 h-12 text-ochre/40 mb-4 animate-pulse" />
        <h3 className="text-lg font-bold text-slate mb-2">Live Event Stream Placeholder</h3>
        <p className="text-sm font-semibold text-slate/60 max-w-md">
          A real-time chart of system events (logins, signups) will be implemented here in future iterations using Recharts and the SSE stream.
        </p>
      </div>
    </div>
  )
}
