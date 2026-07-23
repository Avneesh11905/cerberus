import { createFileRoute, redirect, useNavigate } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { Turnstile } from '@marsidev/react-turnstile'

import { apiClient, extractErrorMessage } from '../lib/api-client'
import { useAuthStore } from '../store/auth'
import { AuthLayout } from '../components/layout/AuthLayout'
import { Input } from '../components/ui/input'
import { InputOTP, InputOTPGroup, InputOTPSlot } from '../components/ui/input-otp'
import { Button } from '../components/ui/button'
import { Label } from '../components/ui/label'

export const Route = createFileRoute('/verify-email')({
  beforeLoad: () => {
    const state = useAuthStore.getState()
    if (state.accessToken) {
      throw redirect({ to: '/' })
    }
    if (!state.unverifiedEmail) {
      throw redirect({ to: '/register' })
    }
  },
  component: VerifyEmailPage,
})

const verifySchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  token: z.string().length(6, 'Token must be exactly 6 digits'),
})

type VerifyData = z.infer<typeof verifySchema>

function VerifyEmailPage() {
  const navigate = useNavigate()
  const unverifiedEmail = useAuthStore(state => state.unverifiedEmail)
  const setUnverifiedEmail = useAuthStore(state => state.setUnverifiedEmail)
  const setVerifiedEmail = useAuthStore(state => state.setVerifiedEmail)
  const otpExpiresAt = useAuthStore(state => state.otpExpiresAt)
  const setOtpExpiresAt = useAuthStore(state => state.setOtpExpiresAt)
  const resendAvailableAt = useAuthStore(state => state.resendAvailableAt)
  const setResendAvailableAt = useAuthStore(state => state.setResendAvailableAt)
  const accessToken = useAuthStore(state => state.accessToken)
  const isCheckingSession = useAuthStore(state => state.isCheckingSession)
  
  const [authMessage, setAuthMessage] = useState<{ type: 'error' | 'success', text: string } | null>(null)
  const [showCaptchaForResend, setShowCaptchaForResend] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [timeLeft, setTimeLeft] = useState<number | null>(null)
  const [isRedirecting, setIsRedirecting] = useState(false)

  useEffect(() => {
    if (accessToken) {
      navigate({ to: '/' })
    }
  }, [accessToken, navigate])

  useEffect(() => {
    if (!resendAvailableAt) {
      setCountdown(0)
      return
    }

    const calculateCountdown = () => {
      const remaining = Math.max(0, Math.floor((resendAvailableAt - Date.now()) / 1000))
      setCountdown(remaining)
      return remaining
    }

    calculateCountdown()
    const timer = setInterval(() => {
      const remaining = calculateCountdown()
      if (remaining <= 0) {
        clearInterval(timer)
      }
    }, 1000)

    return () => clearInterval(timer)
  }, [resendAvailableAt])

  useEffect(() => {
    if (!otpExpiresAt) return

    const calculateTimeLeft = () => {
      const remaining = Math.max(0, Math.floor((otpExpiresAt - Date.now()) / 1000))
      setTimeLeft(remaining)
      return remaining
    }

    calculateTimeLeft()
    const timer = setInterval(() => {
      const remaining = calculateTimeLeft()
      if (remaining <= 0) {
        clearInterval(timer)
      }
    }, 1000)

    return () => clearInterval(timer)
  }, [otpExpiresAt])

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  const { control, register, handleSubmit, formState: { errors }, watch } = useForm<VerifyData>({
    resolver: zodResolver(verifySchema),
    defaultValues: {
      email: unverifiedEmail || ''
    }
  })
  
  const formEmail = watch('email')

  const verifyMutation = useMutation({
    mutationFn: async (data: VerifyData) => {
      const response = await apiClient.post('/auth/verify-email', {
        email: data.email,
        otp: data.token,
      })
      return response.data
    },
    onSuccess: () => {
      setIsRedirecting(true)
      setVerifiedEmail(unverifiedEmail)
      setUnverifiedEmail(null)
      setTimeout(() => navigate({ to: '/login' }), 2000)
    },
    onError: (error: any) => {
      setAuthMessage({ type: 'error', text: extractErrorMessage(error, 'Verification failed') })
    }
  })

  const resendMutation = useMutation({
    mutationFn: async ({ email, token }: { email: string, token: string }) => {
      if (!token) throw new Error("Please complete the captcha to resend")
      const response = await apiClient.post('/auth/verify-email/resend', {
        email: email,
        turnstile_token: token
      })
      return response.data
    },
    onSuccess: (data) => {
      setAuthMessage({ type: 'success', text: 'A new code has been sent to your email.' })
      if (data.expires_in_seconds) {
        setOtpExpiresAt(Date.now() + data.expires_in_seconds * 1000)
      }
      setResendAvailableAt(Date.now() + (data.resend_cooldown_seconds || 60) * 1000)
      setShowCaptchaForResend(false)
    },
    onError: (error: any) => {
      setAuthMessage({ type: 'error', text: extractErrorMessage(error, 'Failed to resend code') })
      setShowCaptchaForResend(false)
    }
  })

  const onSubmit = (data: VerifyData) => {
    setAuthMessage(null)
    verifyMutation.mutate(data)
  }

  if (isCheckingSession || isRedirecting) {
    return (
      <AuthLayout 
        title={isRedirecting ? "Email Verified!" : "Authenticating"} 
        subtitle={isRedirecting ? "Redirecting to login..." : "Please wait..."}
      >
        <div className="flex flex-col items-center justify-center p-8 space-y-4">
          <div className="animate-spin h-10 w-10 border-4 border-slate border-t-transparent rounded-full" />
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Verify your Email" subtitle="Enter your email and the 6-digit code">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" placeholder="you@example.com" {...register('email')} />
          {errors.email && <p className="text-terracotta text-sm font-medium">{errors.email.message}</p>}
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-end">
            <Label htmlFor="token">6-Digit OTP</Label>
            {timeLeft !== null && (
              <span className={`text-xs font-medium ${timeLeft > 0 ? 'text-sage' : 'text-terracotta'}`}>
                {timeLeft > 0 ? `Code expires in ${formatTime(timeLeft)}` : 'Code expired'}
              </span>
            )}
          </div>
          <div className="flex justify-center w-full">
            <Controller
              control={control}
              name="token"
              render={({ field }) => (
                <InputOTP maxLength={6} {...field}>
                  <InputOTPGroup>
                    <InputOTPSlot index={0} />
                    <InputOTPSlot index={1} />
                    <InputOTPSlot index={2} />
                    <InputOTPSlot index={3} />
                    <InputOTPSlot index={4} />
                    <InputOTPSlot index={5} />
                  </InputOTPGroup>
                </InputOTP>
              )}
            />
          </div>
          {errors.token && <p className="text-terracotta text-sm font-medium">{errors.token.message}</p>}
        </div>

        {authMessage && (
          <div className={`p-3 rounded-md border text-sm font-bold text-center ${
            authMessage.type === 'error' 
              ? 'bg-terracotta/10 border-terracotta/20 text-terracotta' 
              : 'bg-sage/10 border-sage/20 text-sage'
          }`}>
            {authMessage.text}
          </div>
        )}

        <Button 
          type="submit" 
          className="w-full mt-4" 
          disabled={verifyMutation.isPending}
        >
          {verifyMutation.isPending ? 'Verifying...' : 'Verify Email'}
        </Button>

        <div className="mt-6 text-center text-sm font-medium text-slate min-h-10 flex items-center justify-center">
          {showCaptchaForResend ? (
            <div className="flex justify-center w-full">
              <span className="text-sm font-medium text-slate">Verifying...</span>
              <Turnstile 
                siteKey={(import.meta.env.VITE_TURNSTILE_SITE_KEY || '').replace(/^["']|["']$/g, '').trim() || '1x00000000000000000000AA'} 
                onSuccess={(token) => {
                  if (formEmail) {
                    resendMutation.mutate({ email: formEmail, token: token });
                  }
                }}
                options={{ size: 'invisible' }}
              />
            </div>
          ) : (
            <div>
              Didn't receive a code?{' '}
              <button 
                type="button"
                onClick={() => {
                  if (!formEmail) {
                    setAuthMessage({ type: 'error', text: 'Please enter your email above to resend the code.' })
                    return
                  }
                  setShowCaptchaForResend(true)
                }}
                disabled={resendMutation.isPending || countdown > 0}
                className="text-slate hover:underline font-bold disabled:opacity-50 disabled:no-underline"
              >
                {resendMutation.isPending ? 'Sending...' : (countdown > 0 ? `Resend (${countdown}s)` : 'Resend')}
              </button>
            </div>
          )}
        </div>
      </form>
    </AuthLayout>
  )
}
