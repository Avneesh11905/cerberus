import { HeadContent, Scripts, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'
import { TanStackDevtools } from '@tanstack/react-devtools'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '../lib/auth'
import { ThemeProvider } from '../components/ThemeProvider'
import appCss from '../styles.css?url'
import { useEffect } from 'react'
import { api } from '../lib/api'
import { toast } from 'sonner'
import { Toaster } from '../components/ui/sonner'

export const queryClient = new QueryClient()
export const Route = createRootRoute({
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
      {
        name: 'description',
        content: 'Cerberus Identity Platform - Professional Auth-as-a-Service',
      },
    ],
    links: [
      {
        rel: 'preconnect',
        href: 'https://fonts.googleapis.com',
      },
      {
        rel: 'preconnect',
        href: 'https://fonts.gstatic.com',
        crossOrigin: 'anonymous',
      },
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap',
      },
      {
        rel: 'icon',
        href: '/logo.webp',
        type: 'image/png',
      },
      {
        rel: 'stylesheet',
        href: appCss,
      },
    ],
  }),
  shellComponent: RootDocument,
})

function RootDocument({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    api.get('/health').catch(() => {
      toast.error('Backend is unreachable', {
        description:
          'Failed to connect to the Cerberus backend. Ensure the server is running.',
      })
    })
  }, [])

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <HeadContent />
      </head>
      <body>
        <ThemeProvider>
          <QueryClientProvider client={queryClient}>
            <AuthProvider>
              {children}
              <Toaster richColors position="top-right" />
              {/* Only render DevTools in development builds — never in production */}
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
            </AuthProvider>
          </QueryClientProvider>
        </ThemeProvider>
        <Scripts />
      </body>
    </html>
  )
}
