import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect, useRef } from 'react'
import { api, setCsrfToken } from '#/lib/api'
import { queryClient } from '#/routes/__root'

export const Route = createFileRoute('/auth/callback')({
  validateSearch: (search: Record<string, unknown>) => ({
    code: (search.code as string | undefined) ?? '',
    new_user: search.new_user === 'true',
  }),
  component: OAuthCallback,
})

function OAuthCallback() {
  const { code, new_user } = Route.useSearch()
  const navigate = useNavigate()
  const attempted = useRef(false)

  useEffect(() => {
    // Guard against React StrictMode double-invocation
    if (attempted.current) return
    attempted.current = true

    if (!code) {
      navigate({ to: '/auth/login', search: { error: 'oauth_failed' } })
      return
    }

    api
      .post<{ is_new_user: boolean; csrf_token: string }>('/auth/exchange', { code })
      .then((res) => {
        // Store the CSRF token in memory — the cookie is host-only on
        // cerberus-api.aymahajan.in so document.cookie on cerberus.aymahajan.in
        // cannot read it. The in-memory value is picked up by the Axios interceptor.
        setCsrfToken(res.data.csrf_token)
        return queryClient.invalidateQueries({ queryKey: ['me'] })
      })
      .then(() => {
        if (new_user) {
          navigate({ to: '/dashboard', search: { new_user: true } })
        } else {
          navigate({ to: '/dashboard' })
        }
      })
      .catch(() => {
        navigate({ to: '/auth/login', search: { error: 'oauth_failed' } })
      })
  }, [code, new_user, navigate])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50 dark:bg-[#0a0a0a] selection:bg-slate-200 dark:selection:bg-slate-800">
      <div className="flex flex-col items-center gap-8 p-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
        <img src="/logo.webp" alt="Cerberus" className="w-20 h-20 animate-pulse select-none pointer-events-none" />

        {/* Spinner */}
        <div className="relative w-10 h-10">
          <div className="absolute inset-0 rounded-full border-2 border-slate-100 dark:border-slate-800" />
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-slate-900 dark:border-t-white animate-spin" />
        </div>

        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Authenticating...</p>
      </div>
    </div>
  )
}
