import { useNavigate, useLocation } from '@tanstack/react-router'
import { useAuthStore } from '../../store/auth'
import {
  LogOut,
  LayoutDashboard,
  FolderKanban,
  Settings,
  Activity,
  Shield,
  Users,
} from 'lucide-react'
import clsx from 'clsx'
import { useAnalyticsStream } from '../../hooks/useAnalyticsStream'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from './tooltip'
import { Avatar, AvatarFallback, AvatarImage } from './avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './dropdown-menu'
import { apiClient } from '../../lib/api-client'

function StreamIndicator() {
  const status = useAnalyticsStream((state) => state.status)

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="flex items-center gap-2 cursor-help">
          <Activity className="w-4 h-4 text-slate/50" />
          <div
            className={clsx(
              'w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.2)]',
              status === 'connected'
                ? 'bg-sage'
                : status === 'connecting'
                  ? 'bg-ochre animate-pulse'
                  : 'bg-terracotta',
            )}
          />
        </div>
      </TooltipTrigger>
      <TooltipContent side="bottom" align="center">
        {status === 'connected'
          ? 'Live Stream Active'
          : status === 'connecting'
            ? 'Connecting...'
            : 'Stream Disconnected'}
      </TooltipContent>
    </Tooltip>
  )
}

export function Navbar() {
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch (e) {
      console.error('Logout request failed', e)
    } finally {
      logout()
    }
  }

  const showStreamIndicator = 
    location.pathname === '/dashboard' || 
    location.pathname === '/superadmin' || 
    (location.pathname.startsWith('/superadmin/tenants/') && location.pathname.endsWith('/analytics'))

  return (
    <header className="h-16 bg-vanilla border-b-2 border-taupe/30 flex items-center justify-between px-6 shrink-0 z-50 relative">
      {/* Left: Logo */}
      <div className="flex items-center flex-1">
        <span
          onClick={() => navigate({ to: '/dashboard' })}
          className="text-xl font-display font-bold text-slate tracking-tight cursor-pointer"
        >
          Cerberus
        </span>
      </div>

      {/* Center: Main Navigation */}
      <nav className="hidden md:flex items-center justify-center gap-8">
        <span
          onClick={() => navigate({ to: '/dashboard' })}
          className={clsx(
            "text-sm font-bold flex items-center gap-2 transition-colors cursor-pointer",
            location.pathname.startsWith('/dashboard') ? "text-slate" : "text-slate/70 hover:text-slate"
          )}
        >
          <LayoutDashboard className="w-4 h-4" />
          Dashboard
        </span>
        <span
          onClick={() => navigate({ to: '/projects' })}
          className={clsx(
            "text-sm font-bold flex items-center gap-2 transition-colors cursor-pointer",
            location.pathname.startsWith('/projects') ? "text-slate" : "text-slate/70 hover:text-slate"
          )}
        >
          <FolderKanban className="w-4 h-4" />
          Projects
        </span>
        <span
          onClick={() => navigate({ to: '/users' })}
          className={clsx(
            "text-sm font-bold flex items-center gap-2 transition-colors cursor-pointer",
            location.pathname.startsWith('/users') ? "text-slate" : "text-slate/70 hover:text-slate"
          )}
        >
          <Users className="w-4 h-4" />
          Global Users
        </span>
        <span
          onClick={() => navigate({ to: '/settings' })}
          className={clsx(
            "text-sm font-bold flex items-center gap-2 transition-colors cursor-pointer",
            location.pathname.startsWith('/settings') ? "text-slate" : "text-slate/70 hover:text-slate"
          )}
        >
          <Settings className="w-4 h-4" />
          Settings
        </span>
      </nav>

      {/* Right: Actions & Profile */}
      <div className="flex items-center justify-end gap-6 flex-1">
        {showStreamIndicator && <StreamIndicator />}
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Avatar className="w-8 h-8 cursor-pointer hover:-translate-y-0.5 hover:-translate-x-0.5 transition-transform outline-none select-none">
              <AvatarImage
                src={user?.picture || undefined}
                alt="Profile"
                className="select-none pointer-events-none"
              />
              <AvatarFallback>
                {(
                  user?.name?.[0] ||
                  user?.email?.[0] ||
                  'U'
                ).toUpperCase()}
              </AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 mt-2">
            <DropdownMenuLabel>
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none text-slate">
                  {typeof user?.name === 'object'
                    ? (user?.name as any)?.value ||
                      JSON.stringify(user?.name)
                    : user?.name || 'User'}
                </p>
                <p className="text-xs leading-none text-slate/50">
                  {typeof user?.email === 'object'
                    ? (user?.email as any)?.value ||
                      JSON.stringify(user?.email)
                    : user?.email}
                </p>
              </div>
            </DropdownMenuLabel>
            {user?.role === 'SUPERADMIN' && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="text-ochre focus:text-ochre cursor-pointer"
                  onClick={() => navigate({ to: '/superadmin' })}
                >
                  <Shield className="w-4 h-4 mr-2" />
                  Superadmin
                </DropdownMenuItem>
              </>
            )}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="text-terracotta focus:text-vanilla focus:bg-terracotta cursor-pointer"
              onClick={handleLogout}
            >
              <LogOut className="w-4 h-4 mr-2" />
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
