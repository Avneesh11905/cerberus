import {
  createFileRoute,
  Link,
  redirect,
  useNavigate,
} from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { Turnstile } from '@marsidev/react-turnstile'
import { Eye, EyeOff } from 'lucide-react'

import { apiClient, API_URL, extractErrorMessage } from '../lib/api-client'
import { useAuthStore } from '../store/auth'
import { AuthLayout } from '../components/layout/AuthLayout'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Label } from '../components/ui/label'
import { GoogleIcon, GithubIcon } from '../components/ui/icons'

export const Route = createFileRoute('/login')({
  validateSearch: z.object({
    redirect: z.string().optional().catch(''),
  }),
  beforeLoad: ({ search }) => {
    if (typeof window === 'undefined') return
    if (useAuthStore.getState().accessToken) {
      throw redirect({ to: search.redirect || '/' })
    }
  },
  component: LoginPage,
})

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginData = z.infer<typeof loginSchema>

function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)
  const accessToken = useAuthStore((state) => state.accessToken)
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null)
  const [authError, setAuthError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  const [pendingAction, setPendingAction] = useState<
    'login' | 'google' | 'github' | null
  >(null)
  const [pendingLoginData, setPendingLoginData] = useState<LoginData | null>(
    null,
  )

  const verifiedEmail = useAuthStore((state) => state.verifiedEmail)

  const search = Route.useSearch()

  // Redirect if token arrives asynchronously (e.g. from root silent refresh)
  useEffect(() => {
    if (accessToken) {
      navigate({ to: search.redirect || '/' })
    }
  }, [accessToken, navigate, search.redirect])

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: verifiedEmail || '',
    },
  })

  const loginMutation = useMutation({
    mutationFn: async (data: LoginData) => {
      if (!turnstileToken) throw new Error('Please complete the captcha')
      const response = await apiClient.post('/auth/login', {
        ...data,
        turnstile_token: turnstileToken,
      })
      return response.data
    },
    onSuccess: (data) => {
      setAuth(data.access_token, data.csrf_token, data.user)
      navigate({ to: search.redirect || '/' })
    },
    onError: (error: unknown) => {
      setAuthError(extractErrorMessage(error, 'Login failed'))
    },
  })

  // Handle pending actions that were waiting for captcha verification
  useEffect(() => {
    if (turnstileToken && pendingAction) {
      if (pendingAction === 'login' && pendingLoginData) {
        loginMutation.mutate(pendingLoginData)
      } else if (pendingAction === 'google' || pendingAction === 'github') {
        window.location.href = `${API_URL}/auth/tenant/login/${pendingAction}`
      }
      setPendingAction(null)
      setPendingLoginData(null)
    }
  }, [turnstileToken, pendingAction, pendingLoginData, loginMutation])

  const onSubmit = (data: LoginData) => {
    setAuthError(null)
    if (!turnstileToken) {
      setPendingAction('login')
      setPendingLoginData(data)
      return
    }

    loginMutation.mutate(data)
  }

  const handleOAuth = (provider: 'google' | 'github') => {
    if (!turnstileToken) {
      setPendingAction(provider)
      return
    }
    window.location.href = `${API_URL}/auth/tenant/login/${provider}`
  }

  if (accessToken) {
    return null
  }

  return (
    <AuthLayout
      title={verifiedEmail ? 'Welcome to Cerberus' : 'Welcome Back'}
      subtitle={
        verifiedEmail
          ? 'Please log in to access your dashboard'
          : 'Log in to Cerberus Dashboard'
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            {...register('email')}
          />
          {errors.email && (
            <p className="text-terracotta text-sm font-medium">
              {errors.email.message}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="password">Password</Label>
            <Link
              to="/forgot-password"
              className="text-sm text-slate font-bold hover:underline"
            >
              Forgot password?
            </Link>
          </div>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              className="pr-10"
              {...register('password')}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate/50 hover:text-slate transition-colors"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          {errors.password && (
            <p className="text-terracotta text-sm font-medium">
              {errors.password.message}
            </p>
          )}
        </div>

        {authError && (
          <div className="p-3 bg-terracotta/10 border border-terracotta/20 rounded-md">
            <p className="text-terracotta text-sm font-bold text-center">
              {authError}
            </p>
          </div>
        )}

        <Turnstile
          siteKey={
            (import.meta.env.VITE_TURNSTILE_SITE_KEY || '')
              .replace(/^["']|["']$/g, '')
              .trim() || '1x00000000000000000000AA'
          }
          onSuccess={(token) => setTurnstileToken(token)}
          options={{ size: 'invisible' }}
        />

        <Button
          type="submit"
          className="w-full mt-4"
          disabled={
            loginMutation.isPending ||
            (pendingAction !== null && pendingAction !== 'login')
          }
        >
          {loginMutation.isPending || pendingAction === 'login' ? (
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Logging in...</span>
            </div>
          ) : (
            'Log in'
          )}
        </Button>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-taupe" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-sand px-2 text-slate font-bold">
              Or continue with
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          <Button
            variant="outline"
            type="button"
            disabled={pendingAction !== null && pendingAction !== 'google'}
            onClick={() => handleOAuth('google')}
            className="flex items-center justify-center space-x-2"
          >
            {pendingAction === 'google' ? (
              <div className="w-4 h-4 border-2 border-slate border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <GoogleIcon className="w-5 h-5" />
                <span className="font-semibold text-[13px] tracking-wide">
                  Google
                </span>
              </>
            )}
          </Button>
          <Button
            variant="outline"
            type="button"
            disabled={pendingAction !== null && pendingAction !== 'github'}
            onClick={() => handleOAuth('github')}
            className="flex items-center justify-center space-x-2"
          >
            {pendingAction === 'github' ? (
              <div className="w-4 h-4 border-2 border-slate border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <GithubIcon className="w-5 h-5 text-slate" />
                <span className="font-semibold text-[13px] tracking-wide">
                  GitHub
                </span>
              </>
            )}
          </Button>
        </div>

        <div className="mt-6 text-center text-sm font-medium text-slate">
          Don't have an account?{' '}
          <Link to="/register" className="text-slate hover:underline font-bold">
            Sign up
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
