import { createFileRoute, redirect, Outlet, Link, useNavigate } from '@tanstack/react-router'
import { useAuthStore } from '../store/auth'
import { LogOut, LayoutDashboard, FolderKanban, Settings, Activity } from 'lucide-react'
import { apiClient } from '../lib/api-client'
import clsx from 'clsx'
import { AnalyticsProvider, useAnalyticsStream } from '../hooks/useAnalyticsStream'

export const Route = createFileRoute('/_protected')({
  beforeLoad: async ({ location }) => {
    const accessToken = useAuthStore.getState().accessToken
    if (!accessToken) {
      throw redirect({
        to: '/login',
        search: {
          redirect: location.href,
        },
      })
    }
  },
  component: ProtectedLayout,
})

function StreamIndicator() {
  const { status } = useAnalyticsStream()
  
  return (
    <div className="flex items-center gap-2" title={status === 'connected' ? 'Live Stream Active' : status === 'connecting' ? 'Connecting...' : 'Stream Disconnected'}>
      <Activity className="w-4 h-4 text-slate/50" />
      <div className={clsx(
        "w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.2)]",
        status === 'connected' ? "bg-sage" : status === 'connecting' ? "bg-ochre animate-pulse" : "bg-terracotta"
      )} />
    </div>
  )
}

function ProtectedLayout() {
  const logout = useAuthStore(state => state.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate({ to: '/login' })
  }

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', to: '/dashboard' },
    { icon: FolderKanban, label: 'Projects', to: '/projects' },
    { icon: Settings, label: 'Settings', to: '/settings' },
  ]

  return (
    <AnalyticsProvider>
      <div className="min-h-screen bg-vanilla flex">
      {/* Sidebar */}
      <aside className="w-64 bg-vanilla border-r-2 border-taupe/30 flex flex-col hidden md:flex shrink-0">
        <div className="h-16 flex items-center px-6 border-b-2 border-taupe/30 shrink-0">
          <span className="text-xl font-display font-bold text-slate tracking-tight">Cerberus</span>
        </div>
        
        <div className="flex flex-col gap-2 p-4 grow">
          {navItems.map((item) => (
            <Link
              key={item.label}
              to={item.to}
              className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate/70 font-bold transition-colors hover:bg-sand/50"
              activeProps={{
                className: "bg-sand text-slate relative after:absolute after:left-0 after:top-2 after:bottom-2 after:w-1 after:bg-slate after:rounded-r-full"
              }}
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </Link>
          ))}
        </div>

        <div className="p-4 mt-auto">
          <button 
            onClick={handleLogout}
            className="flex w-full items-center gap-3 px-4 py-3 rounded-lg text-terracotta font-bold transition-colors hover:bg-terracotta/10"
          >
            <LogOut className="w-5 h-5" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-16 bg-vanilla border-b-2 border-taupe/30 flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center">
            {/* Mobile menu button could go here */}
          </div>
          
          <div className="flex items-center gap-6">
            <StreamIndicator />
            <div className="w-8 h-8 rounded-full bg-sand border-2 border-slate flex items-center justify-center font-bold text-slate text-sm flat-shadow-slate cursor-pointer hover:-translate-y-0.5 hover:-translate-x-0.5 transition-transform">
              U
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto bg-vanilla p-6 sm:p-8">
          <Outlet />
        </main>
      </div>
    </div>
    </AnalyticsProvider>
  )
}
