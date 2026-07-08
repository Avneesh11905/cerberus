import { Link, useLocation } from '@tanstack/react-router'
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from '#/components/ui/sidebar'
import {
  ScrollText,
  Users,
  Settings,
  Shield,
  Globe,
  Key,
  LayoutDashboard,
  Monitor,
  BookOpen,
  Bell,
  User as UserIcon,
} from 'lucide-react'
import { SidebarUserNav } from '#/components/SidebarUserNav'
import { useProjects } from '#/hooks/useProjects'
import { useAuth } from '#/lib/auth'
import { ThemeToggle } from '#/components/ThemeToggle'

export function AppSidebar() {
  const location = useLocation()
  const { projects } = useProjects()
  const { user } = useAuth()

  // Determine context
  const isAdmin = location.pathname.startsWith('/admin')
  const isSettings = location.pathname.startsWith('/settings')
  const isProject = location.pathname.startsWith('/projects/')
  const isDashboard =
    location.pathname === '/dashboard' || location.pathname === '/'

  // Extract projectId if in project context
  let projectId = ''
  if (isProject) {
    const parts = location.pathname.split('/')
    if (parts.length >= 3) {
      projectId = parts[2]
    }
  }

  const currentProject = projects.find((p) => p.id === projectId)

  return (
    <Sidebar
      collapsible="icon"
      className="border-r border-border z-30 flex h-full"
    >
      <SidebarHeader className="border-b border-border p-2 group-data-[collapsible=icon]:p-0 flex flex-col justify-center h-14">
        <Link
          to="/"
          className="flex items-center gap-3 hover:opacity-80 transition-opacity group-data-[collapsible=icon]:justify-center"
        >
          <img
            src="/logo.webp"
            alt="Cerberus"
            className="w-12 h-12 shrink-0 select-none pointer-events-none"
          />
          <span
            className="text-2xl tracking-tight text-slate-900 dark:text-white group-data-[collapsible=icon]:hidden truncate"
            style={{ fontFamily: 'Audiowide, sans-serif' }}
          >
            Cerberus
          </span>
        </Link>
      </SidebarHeader>

      <SidebarContent className="flex-1 overflow-y-auto">
        {isAdmin && (
          <SidebarGroup>
            <SidebarGroupLabel>Admin Console</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={location.pathname === '/admin/tenants'}
                  >
                    <Link to="/admin/tenants">
                      <Users className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Tenants
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={location.pathname === '/admin/logs'}
                  >
                    <Link to="/admin/logs">
                      <ScrollText className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Access Logs
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        {isProject && currentProject && (
          <SidebarGroup>
            <SidebarGroupLabel className="truncate" title={currentProject.name}>
              {currentProject.name}
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={
                      location.hash === '' ||
                      location.hash === '#general' ||
                      location.hash === 'general'
                    }
                  >
                    <Link to={location.pathname} hash="general">
                      <Settings className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        General
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={
                      location.hash === '#providers' ||
                      location.hash === 'providers'
                    }
                  >
                    <Link to={location.pathname} hash="providers">
                      <Shield className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Identity Providers
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={
                      location.hash === '#origins' ||
                      location.hash === 'origins'
                    }
                  >
                    <Link to={location.pathname} hash="origins">
                      <Globe className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Origins & CORS
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={
                      location.hash === '#keys' || location.hash === 'keys'
                    }
                  >
                    <Link to={location.pathname} hash="keys">
                      <Key className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Access Keys & Secrets
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        {isSettings && (
          <SidebarGroup>
            <SidebarGroupLabel>Settings</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={
                      location.hash === '' ||
                      location.hash === '#profile' ||
                      location.hash === 'profile'
                    }
                  >
                    <Link to={location.pathname} hash="profile">
                      <UserIcon className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Profile
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={
                      location.hash === '#preferences' ||
                      location.hash === 'preferences'
                    }
                  >
                    <Link to={location.pathname} hash="preferences">
                      <Bell className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Preferences
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={
                      location.hash === '#security' ||
                      location.hash === 'security'
                    }
                  >
                    <Link to={location.pathname} hash="security">
                      <Shield className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Security
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={
                      location.hash === '#sessions' ||
                      location.hash === 'sessions'
                    }
                  >
                    <Link to={location.pathname} hash="sessions">
                      <Monitor className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Sessions
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        {/* General Navigation link across Dashboard & Settings */}
        {(isSettings || isDashboard || isProject || isAdmin) && (
          <SidebarGroup>
            <SidebarGroupLabel>Navigation</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={location.pathname === '/dashboard'}
                  >
                    <Link to="/dashboard">
                      <LayoutDashboard className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Dashboard
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                {user?.role === 'admin' && (
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild size="lg" isActive={isAdmin}>
                      <Link to="/admin/tenants">
                        <Shield className="h-5 w-5" />
                        <span className="text-base group-data-[collapsible=icon]:hidden">
                          Admin Console
                        </span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )}
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    size="lg"
                    isActive={location.pathname.startsWith('/docs')}
                  >
                    <Link to="/docs">
                      <BookOpen className="h-5 w-5" />
                      <span className="text-base group-data-[collapsible=icon]:hidden">
                        Documentation
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}
      </SidebarContent>

      <SidebarFooter className="border-t border-border p-2 flex flex-col gap-2 shrink-0">
        <div className="flex items-center justify-between group-data-[collapsible=icon]:justify-center px-1">
          <span className="text-sm font-medium text-muted-foreground group-data-[collapsible=icon]:hidden px-2">
            Theme
          </span>
          <ThemeToggle />
        </div>
        <SidebarUserNav />
      </SidebarFooter>
    </Sidebar>
  )
}
