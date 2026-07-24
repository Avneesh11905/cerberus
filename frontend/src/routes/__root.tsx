import { HeadContent, Scripts, createRootRouteWithContext, Outlet, Link } from '@tanstack/react-router'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'
import { TanStackDevtools } from '@tanstack/react-devtools'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { TooltipProvider } from '../components/ui/tooltip'
import { Toaster } from '../components/ui/sonner'
import { useEffect } from 'react'

import appCss from '../styles.css?url'
import { apiClient } from '../lib/api-client'
import { useAuthStore } from '../store/auth'

interface MyRouterContext {
  queryClient: QueryClient
}

export const Route = createRootRouteWithContext<MyRouterContext>()({
  head: () => ({
    meta: [
      {
        charSet: 'utf-8',
      },
      {
        name: 'viewport',
        content: 'width=device-width, initial-scale=1',
      },
      {
        title: 'Cerberus',
      },
    ],
    links: [
      {
        rel: 'stylesheet',
        href: appCss,
      },
    ],
  }),
  component: RootComponent,
  notFoundComponent: () => (
    <div className="min-h-screen bg-vanilla flex flex-col items-center justify-center p-4">
      <div className="flat-card p-8 rounded-xl bg-sand border-taupe text-center max-w-md w-full">
        <h1 className="text-6xl font-display font-bold text-slate mb-4">404</h1>
        <h2 className="text-xl font-bold text-slate mb-2">Page Not Found</h2>
        <p className="text-slate/70 font-medium text-sm mb-8">We couldn't find the page you were looking for.</p>
        <Link to="/" className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-bold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate focus-visible:ring-offset-2 flat-button h-10 px-4 py-2 ring-offset-vanilla">
          Return Home
        </Link>
      </div>
    </div>
  ),
  pendingComponent: () => (
    <div className="min-h-screen bg-vanilla flex flex-col items-center justify-center p-4">
      <div className="w-16 h-16 border-4 border-taupe border-t-terracotta rounded-full animate-spin"></div>
    </div>
  ),
})

function RootComponent() {
  const queryClient = Route.useRouteContext({
    select: (ctx) => ctx.queryClient,
  })

  useEffect(() => {
    // Wait for the next tick to ensure hydration before updating state, though usually fine.
    apiClient.post('/auth/refresh')
      .then(res => {
        if (res.data.access_token) {
          useAuthStore.getState().setAccessToken(res.data.access_token)
        }
      })
      .catch(() => {
        useAuthStore.getState().logout()
      })
      .finally(() => {
        useAuthStore.getState().setIsCheckingSession(false)
      })
  }, [])

  return (
    <html lang="en" className="snap-y snap-proximity scroll-smooth">
      <head>
        <HeadContent />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider delayDuration={100}>
            <Outlet />
            <Toaster />
            {import.meta.env.DEV && (
              <ReactQueryDevtools buttonPosition="bottom-left" />
            )}
          </TooltipProvider>
        </QueryClientProvider>
        
        <TanStackDevtools
          config={{
            position: 'bottom-right',
          }}
          plugins={[
            {
              name: 'Tanstack Router',
              render: <TanStackRouterDevtoolsPanel />,
            },
          ]}
        />
        <Scripts />
      </body>
    </html>
  )
}
