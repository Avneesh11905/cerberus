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

import { apiClient, extractErrorMessage } from '../lib/api-client'
import { AuthLayout } from '../components/layout/AuthLayout'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Label } from '../components/ui/label'
import { useAuthStore } from '../store/auth'

export const Route = createFileRoute('/forgot-password')({
  beforeLoad: () => {
    if (typeof window === 'undefined') return
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      throw redirect({ to: '/' })
    }
  },
  component: ForgotPasswordPage,
})

const forgotSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
})

type ForgotData = z.infer<typeof forgotSchema>

function ForgotPasswordPage() {
  const navigate = useNavigate()
  const [authMessage, setAuthMessage] = useState<{
    type: 'error' | 'success'
    text: string
  } | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotData>({
    resolver: zodResolver(forgotSchema),
  })

  const forgotMutation = useMutation({
    mutationFn: async (data: ForgotData) => {
      const response = await apiClient.post('/auth/password/forgot', data)
      return response.data
    },
    onSuccess: () => {
      setAuthMessage({
        type: 'success',
        text: 'If an account exists, a password reset link has been sent to the email.',
      })
    },
    onError: (error: unknown) => {
      setAuthMessage({
        type: 'error',
        text: extractErrorMessage(error, 'Failed to send reset link'),
      })
    },
  })

  const onSubmit = (data: ForgotData) => {
    setAuthMessage(null)
    forgotMutation.mutate(data)
  }

  return (
    <AuthLayout
      title="Forgot Password"
      subtitle="Enter your email to receive a reset link"
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

        {authMessage && (
          <div
            className={`p-3 rounded-md border text-sm font-bold text-center ${
              authMessage.type === 'error'
                ? 'bg-terracotta/10 border-terracotta/20 text-terracotta'
                : 'bg-sage/10 border-sage/20 text-sage'
            }`}
          >
            {authMessage.text}
          </div>
        )}

        <Button
          type="submit"
          className="w-full mt-4"
          disabled={forgotMutation.isPending}
        >
          {forgotMutation.isPending ? 'Sending...' : 'Send Reset Link'}
        </Button>

        <div className="mt-6 text-center text-sm font-medium text-slate">
          Remembered your password?{' '}
          <Link to="/login" className="text-slate hover:underline font-bold">
            Log in
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
