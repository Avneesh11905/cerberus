import {
  createFileRoute,
  redirect,
  Outlet,
  useLocation,
  useRouter,
} from '@tanstack/react-router'
import { useAuthStore } from '../store/auth'
import clsx from 'clsx'
import { BarChart3, Users, ScrollText, ArrowLeft } from 'lucide-react'
import { Button } from '../components/ui/button'

export const Route = createFileRoute('/_protected/superadmin')({
  beforeLoad: () => {
    if (typeof window === 'undefined') return
    const user = useAuthStore.getState().user
    if (user?.role !== 'SUPERADMIN') {
      throw redirect({ to: '/dashboard' })
    }
  },
  component: SuperadminLayout,
})

function SuperadminLayout() {
  const location = useLocation()
  const router = useRouter()

  const navItems = [
    { name: 'Analytics', href: '/superadmin', icon: BarChart3, exact: true },
    { name: 'Tenants', href: '/superadmin/tenants', icon: Users, exact: false },
    {
      name: 'System Logs',
      href: '/superadmin/logs',
      icon: ScrollText,
      exact: false,
    },
  ]

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-8 w-full">
      <div className="flex items-center gap-4">
        <Button 
          variant="outline" 
          size="icon" 
          className="border-2 border-slate w-10 h-10 rounded-xl"
          onClick={() => router.navigate({ to: '/dashboard' })}
        >
          <ArrowLeft className="w-5 h-5 text-slate" />
        </Button>
        <div>
          <h1 className="text-3xl font-display font-bold text-slate">
            Superadmin Portal
          </h1>
          <p className="text-slate/60 mt-1">
            Platform management and analytics
          </p>
        </div>
      </div>

      {/* Superadmin Sub-navigation */}
      <div className="flex border-b-2 border-taupe/30">
        {navItems.map((item) => {
          const isActive = item.exact
            ? location.pathname === item.href
            : location.pathname.startsWith(item.href)

          return (
            <span
              key={item.name}
              onClick={() => router.navigate({ to: item.href })}
              className={clsx(
                'flex items-center gap-2 px-6 py-3 font-semibold transition-colors border-b-2 -mb-0.5 cursor-pointer',
                isActive
                  ? 'border-ochre text-ochre'
                  : 'border-transparent text-slate/70 hover:text-slate hover:bg-taupe/10',
              )}
            >
              <item.icon className="w-4 h-4" />
              {item.name}
            </span>
          )
        })}
      </div>

      <div className="pt-2">
        <Outlet />
      </div>
    </div>
  )
}
