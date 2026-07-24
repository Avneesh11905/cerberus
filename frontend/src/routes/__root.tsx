import { HeadContent, Scripts, createRootRouteWithContext, Outlet, Link } from '@tanstack/react-router'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'
import { TanStackDevtools } from '@tanstack/react-devtools'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { TooltipProvider } from '../components/ui/tooltip'
import { Toaster } from '../components/ui/sonner'
import { useEffect } from 'react'

import appCss from '../styles.css?url'
import { checkInitialSession } from '../lib/auth-check'

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
  beforeLoad: async () => {
    await checkInitialSession()
  },
  errorComponent: ({ error }) => {
    console.error('Root Error Boundary caught:', error)
    return (
      <div className="min-h-screen bg-vanilla flex flex-col items-center justify-center p-4">
        <div className="flat-card p-8 rounded-xl bg-sand border-taupe text-center max-w-md w-full">
          <h1 className="text-3xl font-display font-bold text-terracotta mb-4">Something went wrong</h1>
          <p className="text-slate/70 font-medium text-sm mb-8">{error?.message || 'An unexpected error occurred.'}</p>
          <a href="/" className="inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-bold bg-slate text-vanilla shadow-[4px_4px_0px_var(--taupe)] h-10 px-4 py-2 hover:-translate-y-0.5 hover:shadow-[6px_6px_0px_var(--taupe)] active:translate-y-0.5 active:translate-x-0.5 active:shadow-[2px_2px_0px_var(--taupe)] transition-all">
            Return Home
          </a>
        </div>
      </div>
    )
  },
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
    checkInitialSession()
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
            <Toaster closeButton />
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
