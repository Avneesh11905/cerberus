import { Link, useNavigate, useLocation } from '@tanstack/react-router'
import { LogOut, Settings, LayoutDashboard, Shield } from 'lucide-react'
import { useAuth } from '#/lib/auth'
import { API_URL } from '#/lib/api'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '#/components/ui/dropdown-menu'
import { Avatar, AvatarFallback, AvatarImage } from '#/components/ui/avatar'
import { Button } from '#/components/ui/button'

export function UserNav() {
  const { user, logout } = useAuth()

  const getAvatarUrl = (url?: string) => {
    if (!url) return undefined
    if (url.startsWith('http') || url.startsWith('data:')) return url
    return `${API_URL}${url.startsWith('/') ? '' : '/'}${url}`
  }
  const navigate = useNavigate()
  const location = useLocation()
  const isLandingPage = location.pathname === '/'

  if (!user) return null

  const displayName = user.name || user.email
  const initial = displayName.charAt(0).toUpperCase()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-8 w-8 rounded-full">
          <Avatar className="h-8 w-8">
            {user.picture ? (
              <AvatarImage src={getAvatarUrl(user.picture)} alt={displayName} />
            ) : null}
            <AvatarFallback>{initial}</AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">{displayName}</p>
            {user.name && (
              <p className="text-xs leading-none text-muted-foreground">
                {user.email}
              </p>
            )}
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        {user.role === 'admin' && (
          <>
            <DropdownMenuItem asChild>
              <Link
                to="/admin/tenants"
                className="cursor-pointer flex items-center"
              >
                <Shield className="mr-2 h-4 w-4" />
                <span>Admin Console</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
          </>
        )}

        {isLandingPage && (
          <DropdownMenuItem asChild>
            <Link to="/dashboard" className="cursor-pointer flex items-center">
              <LayoutDashboard className="mr-2 h-4 w-4" />
              <span>Dashboard</span>
            </Link>
          </DropdownMenuItem>
        )}

        <DropdownMenuItem asChild>
          <Link to="/settings" className="cursor-pointer flex items-center">
            <Settings className="mr-2 h-4 w-4" />
            <span>Settings</span>
          </Link>
        </DropdownMenuItem>

        <DropdownMenuSeparator />
        <DropdownMenuItem
          className="text-destructive focus:bg-destructive/10 cursor-pointer flex items-center"
          onClick={async () => {
            await logout()
            navigate({ to: '/' })
          }}
        >
          <LogOut className="mr-2 h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
