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

export const Route = createFileRoute('/register')({
  beforeLoad: () => {
    if (typeof window === 'undefined') return
    if (useAuthStore.getState().accessToken) {
      throw redirect({ to: '/' })
    }
  },
  component: RegisterPage,
})

const registerSchema = z
  .object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Please enter a valid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  })

type RegisterData = z.infer<typeof registerSchema>

function RegisterPage() {
  const navigate = useNavigate()
  const setUnverifiedEmail = useAuthStore((state) => state.setUnverifiedEmail)
  const setOtpExpiresAt = useAuthStore((state) => state.setOtpExpiresAt)
  const setResendAvailableAt = useAuthStore(
    (state) => state.setResendAvailableAt,
  )
  const accessToken = useAuthStore((state) => state.accessToken)

  const [turnstileToken, setTurnstileToken] = useState<string | null>(null)
  const [authError, setAuthError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  const [pendingAction, setPendingAction] = useState<
    'register' | 'google' | 'github' | null
  >(null)
  const [pendingRegisterData, setPendingRegisterData] =
    useState<RegisterData | null>(null)

  useEffect(() => {
    if (accessToken) {
      navigate({ to: '/' })
    }
  }, [accessToken, navigate])

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterData>({
    resolver: zodResolver(registerSchema),
  })

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterData) => {
      if (!turnstileToken) throw new Error('Please complete the captcha')
      const { confirmPassword, ...backendData } = data
      const response = await apiClient.post('/auth/register', {
        ...backendData,
        turnstile_token: turnstileToken,
      })
      return response.data
    },
    onSuccess: (data, variables) => {
      // Store email in state instead of URL to avoid leaking in history
      setUnverifiedEmail(variables.email)
      if (data.expires_in_seconds) {
        setOtpExpiresAt(Date.now() + data.expires_in_seconds * 1000)
      }
      setResendAvailableAt(null)
      navigate({ to: '/verify-email' })
    },
    onError: (error: unknown) => {
      setAuthError(extractErrorMessage(error, 'Registration failed'))
    },
  })

  // Handle pending actions that were waiting for captcha verification
  useEffect(() => {
    if (turnstileToken && pendingAction) {
      if (pendingAction === 'register' && pendingRegisterData) {
        registerMutation.mutate(pendingRegisterData)
      } else if (pendingAction === 'google' || pendingAction === 'github') {
        window.location.href = `${API_URL}/auth/tenant/login/${pendingAction}`
      }
      setPendingAction(null)
      setPendingRegisterData(null)
    }
  }, [turnstileToken, pendingAction, pendingRegisterData, registerMutation])

  const onSubmit = (data: RegisterData) => {
    setAuthError(null)
    if (!turnstileToken) {
      setPendingAction('register')
      setPendingRegisterData(data)
      return
    }
    registerMutation.mutate(data)
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
      title="Create an Account"
      subtitle="Join Cerberus to manage your data"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            type="text"
            placeholder="John Doe"
            {...register('name')}
          />
          {errors.name && (
            <p className="text-terracotta text-xs font-medium">
              {errors.name.message}
            </p>
          )}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            {...register('email')}
          />
          {errors.email && (
            <p className="text-terracotta text-xs font-medium">
              {errors.email.message}
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Min. 8 chars"
                className="pr-10"
                {...register('password')}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate/50 hover:text-slate transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && (
              <p className="text-terracotta text-xs font-medium">
                {errors.password.message}
              </p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                placeholder="Confirm"
                className="pr-10"
                {...register('confirmPassword')}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate/50 hover:text-slate transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="text-terracotta text-xs font-medium">
                {errors.confirmPassword.message}
              </p>
            )}
          </div>
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
            registerMutation.isPending ||
            (pendingAction !== null && pendingAction !== 'register')
          }
        >
          {registerMutation.isPending || pendingAction === 'register' ? (
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Creating account...</span>
            </div>
          ) : (
            'Sign up'
          )}
        </Button>

        <div className="relative my-4">
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
          Already have an account?{' '}
          <Link to="/login" className="text-slate hover:underline font-bold">
            Log in
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
