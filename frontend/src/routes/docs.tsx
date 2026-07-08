import {
  createFileRoute,
  Outlet,
  Link,
  useLocation,
} from '@tanstack/react-router'
import { ThemeToggle } from '#/components/ThemeToggle'
import { LayoutDashboard } from 'lucide-react'
import { Button } from '#/components/ui/button'
import { UserNav } from '#/components/UserNav'
import { useAuth } from '#/lib/auth'
import { useEffect, useRef } from 'react'

export const Route = createFileRoute('/docs')({
  component: DocsLayout,
})

function DocsLayout() {
  const { user, isLoading } = useAuth()
  const scrollRef = useRef<HTMLDivElement>(null)
  const location = useLocation()

  useEffect(() => {
    // When navigating between doc pages, always reset the scroll container to the top.
    // We use setTimeout to ensure this happens AFTER React has finished rendering the new route
    // and after the browser has attempted its own native scroll restoration.
    const resetScroll = () => {
      if (scrollRef.current) {
        scrollRef.current.scrollTop = 0
      }
    }

    // Fire immediately and also defer
    resetScroll()
    setTimeout(resetScroll, 10)
  }, [location.pathname])

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-50 dark:bg-[#0a0a0a] text-slate-900 dark:text-slate-50 selection:bg-blue-200 selection:text-blue-900 dark:selection:bg-blue-800 dark:selection:text-white">
      {/* Navigation */}
      <nav className="shrink-0 w-full z-50 flex items-center justify-between px-6 py-4 bg-white dark:bg-[#0a0a0a] border-b border-slate-200 dark:border-white/5">
        <div className="flex items-center gap-8">
          <Link
            to="/"
            className="flex items-center gap-3 select-none hover:opacity-80 transition-opacity"
          >
            <img
              src="/logo.webp"
              alt="Cerberus"
              className="w-12 h-12 select-none"
              draggable={false}
            />
            <span
              className="text-2xl tracking-tight"
              style={{ fontFamily: 'Audiowide, sans-serif' }}
            >
              Cerberus
            </span>
          </Link>
        </div>

        <div className="flex items-center gap-4 sm:gap-6">
          <Button
            variant="ghost"
            size="sm"
            asChild
            className="hidden md:flex gap-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
          >
            <Link to="/dashboard">
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>
          </Button>
          <ThemeToggle />
          {isLoading ? (
            <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-800 animate-pulse" />
          ) : user ? (
            <UserNav />
          ) : (
            <div className="flex items-center gap-4">
              <Link
                to="/auth/login"
                className="hidden sm:block text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              >
                Log in
              </Link>
              <Link
                to="/auth/register"
                className="h-9 inline-flex items-center justify-center rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shadow-sm"
              >
                Get API Key
              </Link>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content Area */}
      <div
        ref={scrollRef}
        className="flex-1 min-h-0 w-full relative overflow-y-auto custom-scrollbar id-docs-scroll-container"
      >
        <div className="max-w-360 mx-auto px-4 sm:px-6 lg:px-8 py-12 flex gap-12 relative min-h-max">
          {/* Left Sidebar for Docs Navigation */}
          <aside className="hidden lg:block w-56 shrink-0 self-start sticky top-12 pr-6 border-r border-slate-200 dark:border-slate-800/50">
            <div className="mb-8">
              <h4 className="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider mb-4 font-outfit">
                Documentation
              </h4>
              <div className="flex flex-col gap-2">
                <Link
                  to="/docs"
                  activeProps={{
                    className: 'text-blue-600 dark:text-blue-400 font-medium',
                  }}
                  inactiveProps={{
                    className:
                      'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
                  }}
                  activeOptions={{ exact: true }}
                  className="text-left text-sm transition-colors block py-1"
                >
                  Overview
                </Link>
                <Link
                  to="/docs/setup"
                  activeProps={{
                    className: 'text-blue-600 dark:text-blue-400 font-medium',
                  }}
                  inactiveProps={{
                    className:
                      'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
                  }}
                  className="text-left text-sm transition-colors block py-1"
                >
                  Project Setup
                </Link>
                <div className="flex flex-col mt-2 mb-2">
                  <span className="text-left text-sm font-semibold text-slate-900 dark:text-white block py-1">
                    SDK Reference
                  </span>
                  <div className="flex flex-col pl-4 border-l-2 border-slate-200 dark:border-slate-800 ml-2 mt-1 gap-1">
                    <Link
                      to="/docs/sdk"
                      activeProps={{
                        className:
                          'text-blue-600 dark:text-blue-400 font-medium',
                      }}
                      inactiveProps={{
                        className:
                          'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
                      }}
                      activeOptions={{ exact: true }}
                      className="text-left text-sm transition-colors block py-1"
                    >
                      Getting Started
                    </Link>
                    <Link
                      to="/docs/sdk/auth"
                      activeProps={{
                        className:
                          'text-blue-600 dark:text-blue-400 font-medium',
                      }}
                      inactiveProps={{
                        className:
                          'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
                      }}
                      className="text-left text-sm transition-colors block py-1"
                    >
                      Authentication
                    </Link>
                    <Link
                      to="/docs/sdk/users"
                      activeProps={{
                        className:
                          'text-blue-600 dark:text-blue-400 font-medium',
                      }}
                      inactiveProps={{
                        className:
                          'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
                      }}
                      className="text-left text-sm transition-colors block py-1"
                    >
                      User Management
                    </Link>
                    <Link
                      to="/docs/sdk/react"
                      activeProps={{
                        className:
                          'text-blue-600 dark:text-blue-400 font-medium',
                      }}
                      inactiveProps={{
                        className:
                          'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
                      }}
                      className="text-left text-sm transition-colors block py-1"
                    >
                      React & Routing
                    </Link>
                    <Link
                      to="/docs/sdk/reference"
                      activeProps={{
                        className:
                          'text-blue-600 dark:text-blue-400 font-medium',
                      }}
                      inactiveProps={{
                        className:
                          'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
                      }}
                      className="text-left text-sm transition-colors block py-1"
                    >
                      Advanced Reference
                    </Link>
                  </div>
                </div>
                <Link
                  to="/docs/architecture"
                  activeProps={{
                    className: 'text-blue-600 dark:text-blue-400 font-medium',
                  }}
                  inactiveProps={{
                    className:
                      'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
                  }}
                  className="text-left text-sm transition-colors block py-1"
                >
                  Architecture & Security
                </Link>
              </div>
            </div>
            <div className="mt-12 mb-8 text-xs text-slate-500 dark:text-slate-400">
              &copy; {new Date().getFullYear()} Avneesh Mahajan.
              <br /> Proprietary Software.
            </div>
          </aside>

          {/* Dynamic Nested Content */}
          <Outlet />
        </div>
      </div>
    </div>
  )
}
