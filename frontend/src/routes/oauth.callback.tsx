import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect, useState } from 'react'
import { useAuthStore } from '../store/auth'
import { AuthLayout } from '../components/layout/AuthLayout'
import { apiClient } from '../lib/api-client'
import { z } from 'zod'
import { Button } from '../components/ui/button'

const searchSchema = z.object({
  code: z.string().optional(),
  new_user: z.union([z.string(), z.boolean()]).optional(),
  error: z.string().optional(),
})

export const Route = createFileRoute('/oauth/callback')({
  component: OAuthCallbackPage,
  validateSearch: searchSchema,
})

function OAuthCallbackPage() {
  const search = Route.useSearch()
  const navigate = useNavigate()
  const setAuth = useAuthStore(state => state.setAuth)
  const [error, setError] = useState<string | null>(search.error || null)

  useEffect(() => {
    const completeLogin = async () => {
      try {
        if (search.code) {
          // Redeem the one-time exchange code for session cookies and user info
          const { data } = await apiClient.post('/auth/exchange', { code: search.code });
          setAuth(data.access_token, data.csrf_token, data.user);
          navigate({ to: '/' })
        } else {
          // Fallback if accessed without code but session exists
          const { data } = await apiClient.get('/users/me');
          setAuth('', '', data);
          navigate({ to: '/' })
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'OAuth authentication failed.')
      }
    }
    
    if (!error) {
       completeLogin()
    }
  }, [search, navigate, setAuth, error])

  return (
    <AuthLayout title="Authenticating" subtitle="Please wait while we log you in...">
      <div className="flex flex-col items-center justify-center p-8 space-y-4">
        {error ? (
          <div className="flex flex-col items-center gap-4 w-full max-w-sm">
            <p className="text-terracotta text-sm font-bold text-center">{error}</p>
            <Button onClick={() => navigate({ to: '/login' })} className="w-full mt-4">
              Back to Login
            </Button>
          </div>
        ) : (
          <div className="animate-spin h-10 w-10 border-4 border-slate border-t-transparent rounded-full" />
        )}
      </div>
    </AuthLayout>
  )
}
