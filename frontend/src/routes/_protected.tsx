import { createFileRoute, Outlet, Navigate, redirect } from '@tanstack/react-router'
import { useAuth } from '#/lib/auth'
import { AppSidebar } from '#/components/AppSidebar'
import { SidebarProvider, SidebarInset } from '#/components/ui/sidebar'
import { queryClient } from './__root'
import type { User } from '#/lib/auth'

export const Route = createFileRoute('/_protected')({
  beforeLoad: () => {
    //  Block access at the route level (before component render) for
    // SSR / preloading compatibility. Component-level check in ProtectedLayout
    // handles the authenticated-but-wrong-role cases with a loading state.
    const user = queryClient.getQueryData<User>(['me'])
    if (!user) {
      throw redirect({ to: '/auth/login' })
    }
  },
  component: ProtectedLayout,
})

function ProtectedLayout() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="relative flex min-h-screen bg-slate-50 dark:bg-[#0a0a0a] text-slate-900 dark:text-slate-50 font-sans overflow-hidden items-center justify-center">
        <div className="flex flex-col items-center justify-center animate-pulse gap-6">
          <img src="/logo.webp" alt="Cerberus" className="w-20 h-20 animate-pulse select-none pointer-events-none" />
          <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">Authenticating...</span>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/auth/login" />
  }

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full selection:bg-primary/30 overflow-hidden bg-slate-50 dark:bg-[#0a0a0a] text-slate-900 dark:text-slate-50">
        <AppSidebar />
        <SidebarInset className="flex flex-col flex-1 min-w-0 h-screen overflow-hidden bg-transparent z-10">
          <main className="relative z-10 flex-1 overflow-hidden flex flex-col bg-transparent">
            <Outlet />
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  )
}
