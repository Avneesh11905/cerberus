import { createFileRoute } from '@tanstack/react-router'
import { useAnalyticsStream } from '../hooks/useAnalyticsStream'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { Activity, Users, ShieldAlert, Zap } from 'lucide-react'

export const Route = createFileRoute('/_protected/dashboard')({
  component: DashboardPage,
})



function StatCard({ title, value, icon: Icon, trend, trendUp }: any) {
  return (
    <div className="bg-sand rounded-xl border-2 border-taupe p-6 flat-shadow flex flex-col">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-slate font-bold">{title}</h3>
        <div className="p-2 bg-vanilla rounded-lg border-2 border-taupe">
          <Icon className="w-5 h-5 text-slate" />
        </div>
      </div>
      <div className="text-3xl font-display font-bold text-slate mb-2">{value}</div>
      {trend && (
        <div className={`text-sm font-bold ${trendUp ? 'text-sage' : 'text-terracotta'}`}>
          {trendUp ? '↑' : '↓'} {trend}
        </div>
      )}
    </div>
  )
}

function DashboardPage() {
  const { data } = useAnalyticsStream()

  const timeSeriesData = data?.timeSeries || []
  const endpointsData = data?.endpoints || []

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-display font-bold text-slate mb-2">Dashboard Overview</h1>
          <p className="text-slate/70 font-medium">Real-time metrics for your infrastructure.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Requests (24h)" value={data?.totalRequests || "-"} icon={Activity} trend={data?.trends?.totalRequests} trendUp={data?.trends?.totalRequestsUp} />
        <StatCard title="Active Users" value={data?.activeUsers || "-"} icon={Users} trend={data?.trends?.activeUsers} trendUp={data?.trends?.activeUsersUp} />
        <StatCard title="Error Rate" value={data?.errorRate || "-"} icon={ShieldAlert} trend={data?.trends?.errorRate} trendUp={data?.trends?.errorRateUp} />
        <StatCard title="Avg Latency" value={data?.avgLatency || "-"} icon={Zap} trend={data?.trends?.avgLatency} trendUp={data?.trends?.avgLatencyUp} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <div className="lg:col-span-2 bg-sand rounded-xl border-2 border-taupe p-6 flat-shadow">
          <h2 className="text-xl font-bold text-slate mb-6">Traffic Volume</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeSeriesData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#607274" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#607274" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#B2A59B" vertical={false} />
                <XAxis dataKey="time" stroke="#607274" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#607274" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val / 1000}k`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#FAEED1', border: '2px solid #B2A59B', borderRadius: '0.5rem', color: '#607274', fontWeight: 'bold' }}
                  itemStyle={{ color: '#607274' }}
                />
                <Area type="monotone" dataKey="requests" stroke="#607274" strokeWidth={3} fillOpacity={1} fill="url(#colorRequests)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Side Chart */}
        <div className="bg-sand rounded-xl border-2 border-taupe p-6 flat-shadow">
          <h2 className="text-xl font-bold text-slate mb-6">Top Endpoints</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={endpointsData} layout="vertical" margin={{ top: 0, right: 0, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#B2A59B" horizontal={true} vertical={false} />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" stroke="#607274" fontSize={12} tickLine={false} axisLine={false} width={100} />
                <Tooltip 
                  cursor={{fill: '#FAEED1', opacity: 0.5}}
                  contentStyle={{ backgroundColor: '#FAEED1', border: '2px solid #B2A59B', borderRadius: '0.5rem', color: '#607274', fontWeight: 'bold' }}
                />
                <Bar dataKey="calls" fill="#607274" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
