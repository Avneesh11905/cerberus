import {
  createFileRoute,
  redirect,
  Outlet,
  useLocation,
  Navigate,
} from '@tanstack/react-router'
import { useAuthStore } from '../store/auth'
import type { User } from '../store/auth'
import { isTokenExpired } from '../lib/jwt'
import { refreshClient } from '../lib/api-client'
import { AnalyticsProvider } from '../hooks/useAnalyticsStream'
import { Navbar } from '../components/ui/navbar'
import { ContextMenu, ContextMenuTrigger, ContextMenuContent, ContextMenuItem } from '../components/ui/context-menu'
import { RefreshCcw, ArrowLeft, ArrowRight } from 'lucide-react'

export const Route = createFileRoute('/_protected')({
  beforeLoad: async ({ location }) => {
    if (typeof window === 'undefined') return
    const accessToken = useAuthStore.getState().accessToken
    let isValid = !!accessToken

    if (accessToken && isTokenExpired(accessToken)) {
      try {
        const csrfToken = useAuthStore.getState().csrfToken
        const { data } = await refreshClient.post<{
          access_token: string
          csrf_token?: string
          user?: User
        }>(
          '/auth/refresh',
          {},
          { headers: csrfToken ? { 'X-CSRF': csrfToken } : undefined },
        )
        const newAccessToken = data.access_token
        const newCsrfToken = data?.csrf_token
        if (data.user) {
          useAuthStore
            .getState()
            .setAuth(newAccessToken, newCsrfToken || '', data.user)
        } else {
          useAuthStore.getState().setAccessToken(newAccessToken, newCsrfToken)
        }
        isValid = true
      } catch (err) {
        useAuthStore.getState().logout()
        isValid = false
      }
    }

    if (!isValid) {
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

function ProtectedLayout() {
  const location = useLocation()

  const accessToken = useAuthStore((state) => state.accessToken)

  if (!accessToken) {
    return <Navigate to="/login" search={{ redirect: location.pathname }} />
  }

  let scope: 'tenant' | 'project' | 'system' = 'tenant'
  let projectId: string | undefined = undefined

  if (location.pathname.startsWith('/superadmin')) {
    scope = 'system'
  } else if (location.pathname.startsWith('/projects/') && !location.pathname.endsWith('/settings')) {
    const parts = location.pathname.split('/')
    if (parts.length >= 3 && parts[2] !== '') {
      scope = 'project'
      projectId = parts[2]
    }
  }

  return (
    <AnalyticsProvider scope={scope} projectId={projectId}>
      <div className="fixed inset-0 bg-vanilla flex overflow-hidden">
        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          <Navbar />

          {/* Page Content */}
          <ContextMenu>
            <ContextMenuTrigger asChild>
              <main className="flex-1 overflow-y-auto bg-vanilla p-6 sm:p-8">
                <Outlet />
              </main>
            </ContextMenuTrigger>
            <ContextMenuContent className="w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-[100]">
              <ContextMenuItem
                className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
                onClick={() => window.history.back()}
              >
                <ArrowLeft className="w-4 h-4 mr-2" /> Go Back
              </ContextMenuItem>
              <ContextMenuItem
                className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
                onClick={() => window.history.forward()}
              >
                <ArrowRight className="w-4 h-4 mr-2" /> Go Forward
              </ContextMenuItem>
              <ContextMenuItem
                className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
                onClick={() => window.location.reload()}
              >
                <RefreshCcw className="w-4 h-4 mr-2" /> Reload Page
              </ContextMenuItem>
            </ContextMenuContent>
          </ContextMenu>
        </div>
      </div>
    </AnalyticsProvider>
  )
}
