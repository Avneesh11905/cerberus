import { createFileRoute, Link, useNavigate } from '@tanstack/react-router'
import { useEffect, useState } from 'react'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '#/components/ui/form'
import { Input } from '#/components/ui/input'
import { Button } from '#/components/ui/button'
import { api } from '#/lib/api'

export const Route = createFileRoute('/reset-password')({
  validateSearch: (search: Record<string, unknown>) => ({
    token: typeof search.token === 'string' ? search.token : '',
  }),
  component: ResetPassword,
})

const formSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters long.'),
})

function ResetPassword() {
  const navigate = useNavigate()
  const { token } = Route.useSearch()
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      password: '',
    },
  })

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setError('')
    setMessage('')

    try {
      await api.post('/auth/password/reset', {
        token,
        new_password: values.password,
      })
      setMessage('Your password has been reset. Redirecting to sign in...')
    } catch (err: any) {
      setError(err.message || 'Unable to reset your password.')
    }
  }

  useEffect(() => {
    if (message) {
      const id = window.setTimeout(() => navigate({ to: '/auth/login' }), 1200)
      return () => clearTimeout(id)
    }
  }, [message, navigate])

  return (
    <div className="flex min-h-screen bg-white dark:bg-[#0a0a0a]">
      {/* Left Pane - Branding */}
      <div className="hidden lg:flex w-1/2 flex-col justify-between bg-slate-900 p-12 text-white border-r border-slate-800">
        <div>
          <Link
            to="/"
            className="flex items-center gap-3 w-fit select-none hover:opacity-80 transition-opacity"
          >
            <img
              src="/logo.webp"
              alt="Cerberus"
              className="w-10 h-10 select-none"
              draggable={false}
            />
            <span
              className="text-xl tracking-tight font-medium"
              style={{ fontFamily: 'Audiowide, sans-serif' }}
            >
              Cerberus
            </span>
          </Link>
        </div>
        <div className="max-w-md">
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Secure your account.
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed">
            Choose a strong, unique password to protect your projects and data.
          </p>
        </div>
        <div className="text-sm text-slate-500">
          &copy; {new Date().getFullYear()} Avneesh Mahajan. Proprietary
          Software. All rights reserved.
        </div>
      </div>

      {/* Right Pane - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 lg:p-24">
        <div className="w-full max-w-[400px]">
          <div className="flex flex-col space-y-2 mb-8">
            <h2 className="text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">
              Choose a new password
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Use the reset link from your email to set a new password.
            </p>
          </div>

          {!token && (
            <div className="p-4 mb-6 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl font-medium">
              This reset link is missing a token. Request a new password reset
              link.
            </div>
          )}

          {message && (
            <div className="p-4 mb-6 text-sm text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl font-medium">
              {message}
            </div>
          )}

          {error && (
            <div className="p-4 mb-6 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl font-medium">
              {error}
            </div>
          )}

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium text-slate-900 dark:text-slate-200">
                      New Password
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        disabled={!token}
                        className="h-11 bg-transparent border-slate-300 dark:border-slate-800 focus-visible:ring-slate-400 dark:focus-visible:ring-slate-700 rounded-lg shadow-sm"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button
                type="submit"
                disabled={form.formState.isSubmitting || !token}
                className="w-full h-11 bg-slate-900 hover:bg-slate-800 text-white dark:bg-white dark:hover:bg-slate-200 dark:text-slate-900 font-medium rounded-lg shadow-sm transition-colors mt-2"
              >
                {form.formState.isSubmitting
                  ? 'Resetting...'
                  : 'Reset Password'}
              </Button>
            </form>
          </Form>

          <p className="mt-8 text-center text-sm text-slate-600 dark:text-slate-400">
            Need a new link?{' '}
            <Link
              to="/forgot-password"
              className="font-semibold text-slate-900 dark:text-white hover:underline"
            >
              Request reset
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
