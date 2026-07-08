import { createFileRoute, Link, useNavigate } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
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
import { useAuth } from '#/lib/auth'
import { api, API_URL } from '#/lib/api'

export const Route = createFileRoute('/auth/register')({
  component: Register,
})

const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address.'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

const otpSchema = z.object({
  otp: z.string().length(6, 'Verification code must be 6 digits'),
})

function Register() {
  const [step, setStep] = useState<'register' | 'verify'>('register')
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const { verifyEmail, user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) {
      navigate({ to: '/dashboard' })
    }
  }, [user, navigate])

  const registerForm = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', password: '' },
  })

  const otpForm = useForm<z.infer<typeof otpSchema>>({
    resolver: zodResolver(otpSchema),
    defaultValues: { otp: '' },
  })

  const onRegisterSubmit = async (values: z.infer<typeof registerSchema>) => {
    setError('')
    try {
      await api.post('/auth/register', {
        email: values.email,
        password: values.password,
      })
      setStep('verify')
      setSuccessMsg(
        'Registration successful! Please check your email for the verification code.',
      )
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Registration failed. Please try again.',
      )
    }
  }

  const onOtpSubmit = async (values: z.infer<typeof otpSchema>) => {
    setError('')
    try {
      await verifyEmail({
        email: registerForm.getValues('email'),
        otp: values.otp,
      })
      navigate({ to: '/dashboard' })
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Verification failed. Please check the code.',
      )
    }
  }

  const handleGoogleLogin = () =>
    (window.location.href = `${API_URL}/auth/login/google`)
  const handleGithubLogin = () =>
    (window.location.href = `${API_URL}/auth/login/github`)

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
            Start your journey.
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed">
            Create an account to integrate advanced authentication and
            centralized management into your products in minutes.
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
              {step === 'register' ? 'Create an account' : 'Check your email'}
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {step === 'register'
                ? 'Enter your details below to get started.'
                : `We sent an OTP to ${registerForm.getValues('email')}`}
            </p>
          </div>

          {successMsg && (
            <div className="p-4 mb-6 text-sm text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl font-medium">
              {successMsg}
            </div>
          )}

          {step === 'register' ? (
            <>
              <Form {...registerForm}>
                <form
                  onSubmit={registerForm.handleSubmit(onRegisterSubmit)}
                  className="space-y-5"
                >
                  <FormField
                    control={registerForm.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium text-slate-900 dark:text-slate-200">
                          Email Address
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder="you@company.com"
                            type="email"
                            className="h-11 bg-transparent border-slate-300 dark:border-slate-800 focus-visible:ring-slate-400 dark:focus-visible:ring-slate-700 rounded-lg shadow-sm"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={registerForm.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium text-slate-900 dark:text-slate-200">
                          Password
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="password"
                            placeholder="Minimum 8 characters"
                            className="h-11 bg-transparent border-slate-300 dark:border-slate-800 focus-visible:ring-slate-400 dark:focus-visible:ring-slate-700 rounded-lg shadow-sm"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  {error && (
                    <p className="text-sm font-medium text-red-600 dark:text-red-400">
                      {error}
                    </p>
                  )}

                  <Button
                    type="submit"
                    disabled={registerForm.formState.isSubmitting}
                    className="w-full h-11 bg-slate-900 hover:bg-slate-800 text-white dark:bg-white dark:hover:bg-slate-200 dark:text-slate-900 font-medium rounded-lg shadow-sm transition-colors mt-2"
                  >
                    {registerForm.formState.isSubmitting
                      ? 'Creating account...'
                      : 'Start for free'}
                  </Button>
                </form>
              </Form>

              <div className="relative my-8">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200 dark:border-slate-800" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="px-4 bg-white dark:bg-[#0a0a0a] text-slate-500 font-medium tracking-wider">
                    Or sign up with
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleGoogleLogin}
                  className="h-11 bg-transparent border-slate-300 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900 rounded-lg font-medium text-slate-700 dark:text-slate-300 shadow-sm transition-colors"
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="currentColor"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  Google
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleGithubLogin}
                  className="h-11 bg-transparent border-slate-300 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900 rounded-lg font-medium text-slate-700 dark:text-slate-300 shadow-sm transition-colors"
                >
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      fillRule="evenodd"
                      d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                      clipRule="evenodd"
                    />
                  </svg>
                  GitHub
                </Button>
              </div>
            </>
          ) : (
            <Form {...otpForm}>
              <form
                onSubmit={otpForm.handleSubmit(onOtpSubmit)}
                className="space-y-5"
              >
                <FormField
                  control={otpForm.control}
                  name="otp"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium text-slate-900 dark:text-slate-200">
                        6-Digit Verification Code
                      </FormLabel>
                      <FormControl>
                        <Input
                          placeholder="000000"
                          maxLength={6}
                          className="h-14 text-center tracking-[0.5em] font-mono text-2xl bg-transparent border-slate-300 dark:border-slate-800 focus-visible:ring-slate-400 dark:focus-visible:ring-slate-700 rounded-lg shadow-sm"
                          {...field}
                          onChange={(e) =>
                            field.onChange(
                              e.target.value.replace(/\D/g, '').slice(0, 6),
                            )
                          }
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                {error && (
                  <p className="text-sm font-medium text-red-600 dark:text-red-400">
                    {error}
                  </p>
                )}

                <Button
                  type="submit"
                  disabled={otpForm.formState.isSubmitting}
                  className="w-full h-11 bg-slate-900 hover:bg-slate-800 text-white dark:bg-white dark:hover:bg-slate-200 dark:text-slate-900 font-medium rounded-lg shadow-sm transition-colors mt-2"
                >
                  {otpForm.formState.isSubmitting
                    ? 'Verifying...'
                    : 'Verify & Enter'}
                </Button>
              </form>
            </Form>
          )}

          <p className="mt-8 text-center text-sm text-slate-600 dark:text-slate-400">
            Already have an account?{' '}
            <Link
              to="/auth/login"
              className="font-semibold text-slate-900 dark:text-white hover:underline"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
