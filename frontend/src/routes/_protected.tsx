import { createFileRoute, redirect, Outlet, Link, useNavigate, useLocation, Navigate } from '@tanstack/react-router'
import { useAuthStore } from '../store/auth'
import { checkInitialSession } from '../lib/auth-check'
import { LogOut, LayoutDashboard, FolderKanban, Settings, Activity } from 'lucide-react'
import clsx from 'clsx'
import { AnalyticsProvider, useAnalyticsStream } from '../hooks/useAnalyticsStream'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../components/ui/tooltip'
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu'

export const Route = createFileRoute('/_protected')({
  beforeLoad: async ({ location }) => {
    if (typeof window === 'undefined') return;
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
  const status = useAnalyticsStream(state => state.status)
  
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="flex items-center gap-2 cursor-help">
          <Activity className="w-4 h-4 text-slate/50" />
          <div className={clsx(
            "w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.2)]",
            status === 'connected' ? "bg-sage" : status === 'connecting' ? "bg-ochre animate-pulse" : "bg-terracotta"
          )} />
        </div>
      </TooltipTrigger>
      <TooltipContent side="bottom" align="center">
        {status === 'connected' ? 'Live Stream Active' : status === 'connecting' ? 'Connecting...' : 'Stream Disconnected'}
      </TooltipContent>
    </Tooltip>
  )
}

function ProtectedLayout() {
  const user = useAuthStore(state => state.user)
  const isCheckingSession = useAuthStore(state => state.isCheckingSession)
  const logout = useAuthStore(state => state.logout)
  const navigate = useNavigate()
  const location = useLocation()
  const isSettings = location.pathname.startsWith('/settings')

  const accessToken = useAuthStore(state => state.accessToken)

  if (isCheckingSession) {
    return (
      <div className="min-h-screen bg-vanilla flex flex-col items-center justify-center p-4">
        <div className="w-16 h-16 border-4 border-taupe border-t-terracotta rounded-full animate-spin"></div>
      </div>
    )
  }

  if (!accessToken) {
    return <Navigate to="/login" search={{ redirect: location.pathname }} />
  }

  const handleLogout = () => {
    logout()
    navigate({ to: '/login' })
  }

  return (
    <AnalyticsProvider>
      <div className="fixed inset-0 bg-vanilla flex overflow-hidden">

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-16 bg-vanilla border-b-2 border-taupe/30 flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center">
            {!isSettings && (
              <Link to="/dashboard" className="text-xl font-display font-bold text-slate tracking-tight">Cerberus</Link>
            )}
          </div>
          
          <div className="flex items-center gap-6">
            {!isSettings && <StreamIndicator />}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Avatar 
                  className="w-8 h-8 cursor-pointer hover:-translate-y-0.5 hover:-translate-x-0.5 transition-transform outline-none select-none"
                >
                  <AvatarImage src={user?.picture || undefined} alt="Profile" className="select-none pointer-events-none" />
                  <AvatarFallback>{(user?.name?.[0] || user?.email?.[0] || 'U').toUpperCase()}</AvatarFallback>
                </Avatar>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 mt-2">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none text-slate">
                      {typeof user?.name === 'object' ? (user?.name as any)?.value || JSON.stringify(user?.name) : (user?.name || 'User')}
                    </p>
                    <p className="text-xs leading-none text-slate/50">
                      {typeof user?.email === 'object' ? (user?.email as any)?.value || JSON.stringify(user?.email) : user?.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                {!location.pathname.startsWith('/dashboard') && (
                  <DropdownMenuItem onClick={() => navigate({ to: '/dashboard' })}>
                    <LayoutDashboard className="w-4 h-4 mr-2" />
                    Dashboard
                  </DropdownMenuItem>
                )}
                {!location.pathname.startsWith('/projects') && (
                  <DropdownMenuItem onClick={() => navigate({ to: '/projects' })}>
                    <FolderKanban className="w-4 h-4 mr-2" />
                    Projects
                  </DropdownMenuItem>
                )}
                {!isSettings && (
                  <DropdownMenuItem onClick={() => navigate({ to: '/settings' })}>
                    <Settings className="w-4 h-4 mr-2" />
                    Settings
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-terracotta focus:text-vanilla focus:bg-terracotta" onClick={handleLogout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto bg-vanilla p-6 sm:p-8">
          <Outlet />
        </main>
      </div>
    </div>
    </AnalyticsProvider>
  )
}
