import { createFileRoute, Outlet, useLocation } from '@tanstack/react-router'
import { SidebarTrigger } from '#/components/ui/sidebar'
import { ScrollArea } from '#/components/ui/scroll-area'

export const Route = createFileRoute('/_protected/admin')({
  component: AdminLayout,
})

function AdminLayout() {
  const location = useLocation()

  return (
    <div className="flex flex-col h-full bg-transparent">
      <header className="flex h-14 items-center gap-4 border-b border-slate-200/50 dark:border-slate-800/50 backdrop-blur-md bg-white/70 dark:bg-[#0a0a0a]/70 px-4 shrink-0 sticky top-0 z-50">
        <SidebarTrigger />
        <h1 className="font-semibold text-lg">
          {location.pathname === '/admin/tenants'
            ? 'Tenants Management'
            : 'System Access Logs'}
        </h1>
      </header>
      <ScrollArea className="flex-1 w-full">
        <main className="p-6">
          <Outlet />
        </main>
      </ScrollArea>
    </div>
  )
}
