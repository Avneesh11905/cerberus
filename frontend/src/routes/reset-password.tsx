import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'

import { apiClient, extractErrorMessage } from '../lib/api-client'
import { AuthLayout } from '../components/layout/AuthLayout'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Label } from '../components/ui/label'

const searchSchema = z.object({
  token: z.string().optional(),
})

export const Route = createFileRoute('/reset-password')({
  component: ResetPasswordPage,
  validateSearch: searchSchema,
})

const resetSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

type ResetData = z.infer<typeof resetSchema>

function ResetPasswordPage() {
  const search = Route.useSearch()
  const navigate = useNavigate()
  const [authMessage, setAuthMessage] = useState<{ type: 'error' | 'success', text: string } | null>(null)

  const { register, handleSubmit, formState: { errors } } = useForm<ResetData>({
    resolver: zodResolver(resetSchema)
  })

  const resetMutation = useMutation({
    mutationFn: async (data: ResetData) => {
      const response = await apiClient.post('/auth/password/reset', {
        token: search.token,
        new_password: data.password
      })
      return response.data
    },
    onSuccess: () => {
      setAuthMessage({ type: 'success', text: 'Password reset successfully! You can now log in.' })
      setTimeout(() => navigate({ to: '/login' }), 2000)
    },
    onError: (error: any) => {
      setAuthMessage({ type: 'error', text: extractErrorMessage(error, 'Failed to reset password') })
    }
  })

  const onSubmit = (data: ResetData) => {
    if (!search.token) {
      setAuthMessage({ type: 'error', text: 'Missing reset token in URL.' })
      return
    }
    setAuthMessage(null)
    resetMutation.mutate(data)
  }

  return (
    <AuthLayout title="Reset Password" subtitle="Enter your new password below">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="password">New Password</Label>
          <Input id="password" type="password" placeholder="Min. 8 characters" {...register('password')} />
          {errors.password && <p className="text-terracotta text-sm font-medium">{errors.password.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword">Confirm Password</Label>
          <Input id="confirmPassword" type="password" {...register('confirmPassword')} />
          {errors.confirmPassword && <p className="text-terracotta text-sm font-medium">{errors.confirmPassword.message}</p>}
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
          disabled={resetMutation.isPending || !search.token}
        >
          {resetMutation.isPending ? 'Resetting...' : 'Reset Password'}
        </Button>
      </form>
    </AuthLayout>
  )
}
