import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState, useEffect, useMemo } from 'react'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import {
  Settings,
  Shield,
  User as UserIcon,
  LogOut,
  Trash2,
  Smartphone,
  Monitor,
  Check,
  AlertTriangle,
  ArrowLeft,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

import { useAuthStore } from '../store/auth'
import { updateProfile, deleteMe, getMe } from '../api/users'
import {
  updatePassword,
  getSessions,
  revokeSession,
  revokeAllSessions,
} from '../api/auth'
import { extractErrorMessage } from '../lib/api-client'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '../components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Checkbox } from '../components/ui/checkbox'
import { GoogleIcon, GithubIcon } from '../components/ui/icons'

export const Route = createFileRoute('/_protected/settings')({
  component: SettingsPage,
})

const profileSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  picture: z.string().url('Must be a valid URL').optional().or(z.literal('')),
})
type ProfileFormData = z.infer<typeof profileSchema>

function ProfileTab() {
  const user = useAuthStore((state) => state.user)
  const setUser = useAuthStore((state) => state.setUser)
  const queryClient = useQueryClient()
  const [isSaved, setIsSaved] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: user?.name || '',
      picture: user?.picture || '',
    },
  })

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: getMe,
  })

  const hasPassword = profile ? profile.login_methods?.includes('local') : true

  // Sync fetched profile with local form and Zustand store
  useEffect(() => {
    if (profile) {
      reset({
        name: profile.name || '',
        picture: profile.picture || '',
      })
      const currentUser = useAuthStore.getState().user
      if (currentUser) {
        setUser({ ...currentUser, ...profile })
      }
    }
  }, [profile, reset, setUser])

  const updateProfileMutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: (data) => {
      setUser({ ...user!, ...data })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setIsSaved(true)
      setTimeout(() => setIsSaved(false), 2000)
    },
    onError: (err: unknown) => {
      toast.error(extractErrorMessage(err, 'Failed to update profile'))
    },
  })

  const receiveUpdatesMutation = useMutation({
    mutationFn: updateProfile,
    onMutate: async (newData) => {
      await queryClient.cancelQueries({ queryKey: ['profile'] })
      const previousProfile = queryClient.getQueryData(['profile'])
      queryClient.setQueryData(['profile'], (old: any) => ({
        ...old,
        ...newData,
      }))
      return { previousProfile }
    },
    onSuccess: (data) => {
      setUser({ ...user!, ...data })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
    onError: (err: unknown, _newData, context) => {
      if (context?.previousProfile) {
        queryClient.setQueryData(['profile'], context.previousProfile)
      }
      toast.error(extractErrorMessage(err, 'Failed to update settings'))
    },
  })

  if (isLoading) {
    return (
      <Card className="flat-card border-2 flex items-center justify-center p-12">
        <div className="animate-spin h-8 w-8 border-4 border-slate border-t-transparent rounded-full" />
      </Card>
    )
  }

  const pictureUrl = watch('picture')

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
      {!hasPassword && (
        <Card className="flat-card border-2 border-sunflower/50 bg-sunflower/10">
          <CardContent className="flex items-start gap-3 p-4">
            <AlertTriangle className="w-5 h-5 mt-0.5 shrink-0 text-sunflower" />
            <div className="text-sm font-bold text-slate">
              Your account doesn't have a password set. We highly recommend
              setting a password in the Security tab to fully secure your
              account.
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="flat-card border-2">
        <form
          onSubmit={handleSubmit((data) => updateProfileMutation.mutate(data))}
        >
          <CardHeader>
            <CardTitle>Profile Details</CardTitle>
            <CardDescription>Update your personal information.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="picture">Profile Picture</Label>
              <div className="flex items-start gap-4">
                <Avatar className="w-16 h-16 border-2 border-slate shadow-[2px_2px_0px_rgba(30,41,59,1)] shrink-0">
                  <AvatarImage src={pictureUrl || user?.picture || ''} />
                  <AvatarFallback className="bg-sage/20 text-sage text-2xl font-black">
                    {(user?.name || 'U')[0].toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 space-y-2 mt-1">
                  <Input
                    id="picture"
                    placeholder="https://example.com/avatar.jpg"
                    {...register('picture')}
                    className={
                      errors.picture
                        ? 'border-terracotta focus-visible:ring-terracotta'
                        : ''
                    }
                  />
                  {errors.picture && (
                    <p className="text-sm font-bold text-terracotta">
                      {errors.picture.message}
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  value={profile?.email || user?.email || ''}
                  disabled
                  className="bg-taupe/10 cursor-not-allowed"
                />
                <p className="text-xs font-bold text-slate/50">
                  Email cannot be changed via the API directly.
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">Display Name</Label>
                <Input
                  id="name"
                  {...register('name')}
                  className={
                    errors.name
                      ? 'border-terracotta focus-visible:ring-terracotta'
                      : ''
                  }
                />
                {errors.name && (
                  <p className="text-sm font-bold text-terracotta">
                    {errors.name.message}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Account Details</Label>
              <div className="flex flex-wrap gap-6 p-4 rounded-xl bg-vanilla border-2 border-taupe/30">
                <div className="flex flex-col gap-1.5">
                  <span className="text-xs font-bold text-slate/50 uppercase tracking-wider">
                    Login Methods
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {profile?.login_methods?.map((method: string) => (
                      <span
                        key={method}
                        className="flex items-center gap-1.5 px-3 py-1 bg-slate/10 text-slate text-[10px] uppercase tracking-wider font-bold rounded-full border-2 border-slate/20"
                      >
                        {method.toLowerCase() === 'google' && (
                          <GoogleIcon className="w-3 h-3" />
                        )}
                        {method.toLowerCase() === 'github' && (
                          <GithubIcon className="w-3 h-3" />
                        )}
                        {method}
                      </span>
                    ))}
                    {(!profile?.login_methods ||
                      profile.login_methods.length === 0) && (
                      <span className="text-sm font-medium text-slate/50">
                        None
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 rounded-xl border-2 border-taupe/30 bg-vanilla">
              <Checkbox
                id="receive_updates"
                checked={profile?.receive_updates ?? false}
                onCheckedChange={(checked) => {
                  const newValue = checked === true
                  receiveUpdatesMutation.mutate({ receive_updates: newValue })
                }}
                className="mt-1"
              />
              <div className="space-y-1">
                <Label htmlFor="receive_updates" className="cursor-pointer">
                  Receive Email Updates
                </Label>
                <p className="text-xs font-bold text-slate/60">
                  Opt-in to receive product updates, security alerts, and
                  newsletters.
                </p>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-end border-t-2 border-taupe/20 pt-6">
            <Button
              type="submit"
              variant="primary"
              disabled={updateProfileMutation.isPending}
            >
              <AnimatePresence mode="wait">
                {isSaved ? (
                  <motion.div
                    key="saved"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-center gap-2"
                  >
                    <Check className="w-4 h-4" /> Saved!
                  </motion.div>
                ) : (
                  <motion.div
                    key="save"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    {updateProfileMutation.isPending
                      ? 'Saving...'
                      : 'Save Changes'}
                  </motion.div>
                )}
              </AnimatePresence>
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}

const getPasswordSchema = (hasPassword: boolean) =>
  z
    .object({
      current_password: hasPassword
        ? z.string().min(1, 'Current password is required')
        : z.string().optional(),
      new_password: z.string().min(8, 'Password must be at least 8 characters'),
      confirm_password: z.string().min(1, 'Please confirm password'),
    })
    .refine((data) => data.new_password === data.confirm_password, {
      message: "Passwords don't match",
      path: ['confirm_password'],
    })

type PasswordFormData = {
  current_password?: string | undefined
  new_password: string
  confirm_password: string
}

function ChangePasswordCard() {
  const { data: profile } = useQuery({ queryKey: ['profile'], queryFn: getMe })
  const hasPassword = profile ? profile.login_methods?.includes('local') : true
  const dynamicSchema = useMemo(
    () => getPasswordSchema(hasPassword ?? true),
    [hasPassword],
  )

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PasswordFormData>({
    resolver: zodResolver(dynamicSchema) as any,
  })

  const queryClient = useQueryClient()

  const passwordMutation = useMutation({
    mutationFn: updatePassword,
    onSuccess: () => {
      toast.success(
        hasPassword
          ? 'Password updated successfully'
          : 'Password set successfully',
      )
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      reset()
    },
    onError: (err: unknown) => {
      toast.error(extractErrorMessage(err, 'Failed to update password'))
    },
  })

  return (
    <Card className="flat-card border-2">
      <form onSubmit={handleSubmit((data) => passwordMutation.mutate(data))}>
        <CardHeader>
          <CardTitle>
            {hasPassword ? 'Change Password' : 'Set Password'}
          </CardTitle>
          <CardDescription>
            {hasPassword
              ? 'Ensure your account is using a long, random password to stay secure.'
              : 'Add a password to your account so you can log in with email and password.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {hasPassword && (
            <div className="space-y-2">
              <Label htmlFor="current_password">Current Password</Label>
              <Input
                id="current_password"
                type="password"
                {...register('current_password')}
                className={
                  errors.current_password
                    ? 'border-terracotta focus-visible:ring-terracotta'
                    : ''
                }
              />
              {errors.current_password && (
                <p className="text-sm font-bold text-terracotta">
                  {errors.current_password.message}
                </p>
              )}
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="new_password">New Password</Label>
            <Input
              id="new_password"
              type="password"
              {...register('new_password')}
              className={
                errors.new_password
                  ? 'border-terracotta focus-visible:ring-terracotta'
                  : ''
              }
            />
            {errors.new_password && (
              <p className="text-sm font-bold text-terracotta">
                {errors.new_password.message}
              </p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm_password">Confirm New Password</Label>
            <Input
              id="confirm_password"
              type="password"
              {...register('confirm_password')}
              className={
                errors.confirm_password
                  ? 'border-terracotta focus-visible:ring-terracotta'
                  : ''
              }
            />
            {errors.confirm_password && (
              <p className="text-sm font-bold text-terracotta">
                {errors.confirm_password.message}
              </p>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex justify-end border-t-2 border-taupe/20 pt-6">
          <Button
            type="submit"
            variant="primary"
            disabled={passwordMutation.isPending}
          >
            {passwordMutation.isPending
              ? 'Updating...'
              : hasPassword
                ? 'Update Password'
                : 'Set Password'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}

const parseUserAgent = (ua?: string | null) => {
  if (!ua) return 'Unknown Device'
  let os = 'Unknown OS'
  if (ua.includes('Win')) os = 'Windows'
  else if (ua.includes('Mac')) os = 'macOS'
  else if (ua.includes('Linux')) os = 'Linux'
  else if (ua.includes('iPhone') || ua.includes('iPad')) os = 'iOS'
  else if (ua.includes('Android')) os = 'Android'

  let browser = 'Browser'
  if (ua.includes('Firefox')) browser = 'Firefox'
  else if (ua.includes('Edg')) browser = 'Edge'
  else if (ua.includes('Chrome')) browser = 'Chrome'
  else if (ua.includes('Safari')) browser = 'Safari'

  return `${browser} on ${os}`
}

function ActiveSessionsCard() {
  const queryClient = useQueryClient()

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: getSessions,
  })

  const revokeMutation = useMutation({
    mutationFn: revokeSession,
    onSuccess: () => {
      toast.success('Session revoked')
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
    onError: (err: unknown) =>
      toast.error(extractErrorMessage(err, 'Failed to revoke session')),
  })

  const revokeAllMutation = useMutation({
    mutationFn: revokeAllSessions,
    onSuccess: () => {
      toast.success('All other sessions revoked')
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
    onError: (err: unknown) =>
      toast.error(extractErrorMessage(err, 'Failed to revoke all sessions')),
  })

  return (
    <Card className="flat-card border-2">
      <CardHeader className="flex flex-col sm:flex-row sm:items-start justify-between space-y-4 sm:space-y-0">
        <div className="space-y-1.5">
          <CardTitle>Active Sessions</CardTitle>
          <CardDescription>
            Manage devices that are currently logged into your account.
          </CardDescription>
        </div>
        <Button
          variant="outline"
          onClick={() => revokeAllMutation.mutate()}
          disabled={
            revokeAllMutation.isPending || !sessions || sessions.length <= 1
          }
          className="shrink-0"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Log out all devices
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center p-8">
            <div className="w-8 h-8 border-4 border-slate border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="space-y-4">
            {sessions?.map((session: any) => (
              <div
                key={session.family_id}
                className="flex flex-col sm:flex-row sm:items-center justify-between p-4 border-2 border-taupe rounded-xl bg-vanilla gap-4 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-sand border-2 border-taupe flex items-center justify-center shrink-0">
                    {session.user_agent?.includes('Mobi') ? (
                      <Smartphone className="w-5 h-5 text-slate" />
                    ) : (
                      <Monitor className="w-5 h-5 text-slate" />
                    )}
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <p className="font-bold text-slate">
                        {parseUserAgent(session.user_agent)}
                      </p>
                      {session.auth_provider && (
                        <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate/10 text-slate text-[10px] uppercase tracking-wider font-bold border-2 border-slate/20">
                          {session.auth_provider.toLowerCase() === 'google' && (
                            <GoogleIcon className="w-3 h-3" />
                          )}
                          {session.auth_provider.toLowerCase() === 'github' && (
                            <GithubIcon className="w-3 h-3" />
                          )}
                          {session.auth_provider}
                        </span>
                      )}
                      {session.is_current && (
                        <span className="px-2 py-0.5 rounded-full bg-sage/20 text-sage text-[10px] uppercase tracking-wider font-bold border-2 border-sage/30">
                          Current
                        </span>
                      )}
                    </div>
                    <p className="text-sm font-medium text-slate/60">
                      {session.ip_address} • Last active{' '}
                      {session.last_active
                        ? new Date(session.last_active).toLocaleString()
                        : 'Unknown'}
                    </p>
                  </div>
                </div>
                {!session.is_current && (
                  <Button
                    variant="destructive"
                    onClick={() => revokeMutation.mutate(session.family_id)}
                    disabled={revokeMutation.isPending}
                  >
                    Revoke
                  </Button>
                )}
              </div>
            ))}
            {(!sessions || sessions.length === 0) && (
              <p className="text-center text-slate/50 font-medium py-4">
                No active sessions found.
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function DeleteAccountCard() {
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()

  const deleteMutation = useMutation({
    mutationFn: deleteMe,
    onSuccess: () => {
      toast.success('Account deleted successfully')
      logout()
      navigate({ to: '/login' })
    },
    onError: (err: unknown) =>
      toast.error(extractErrorMessage(err, 'Failed to delete account')),
  })

  return (
    <Card className="bg-terracotta/10 border-2 border-terracotta shadow-[4px_4px_0px_var(--terracotta)]">
      <CardHeader>
        <CardTitle className="text-terracotta flex items-center gap-2">
          <AlertTriangle className="w-6 h-6" />
          Danger Zone
        </CardTitle>
        <CardDescription className="text-terracotta/80 font-bold text-sm">
          Permanently delete your account and all associated data. This action
          cannot be undone.
        </CardDescription>
      </CardHeader>
      <CardFooter className="border-t-2 border-terracotta/20 pt-6">
        <Button
          variant="destructive"
          onClick={() => {
            if (
              window.confirm(
                'Are you absolutely sure you want to delete your account? This is irreversible.',
              )
            ) {
              deleteMutation.mutate()
            }
          }}
          disabled={deleteMutation.isPending}
          className="flex items-center gap-2"
        >
          <Trash2 className="w-4 h-4" />
          {deleteMutation.isPending ? 'Deleting...' : 'Delete Account'}
        </Button>
      </CardFooter>
    </Card>
  )
}

function SecurityTab() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
      <ActiveSessionsCard />
      <ChangePasswordCard />
      <DeleteAccountCard />
    </div>
  )
}

function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'security'>('profile')
  const user = useAuthStore((state) => state.user)

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-20">
      <div className="flex items-center gap-3 mb-6">
        <Button 
          variant="outline" 
          size="icon" 
          className="border-2 border-slate w-10 h-10 rounded-xl"
          onClick={() => router.navigate({ to: '/dashboard' })}
        >
          <ArrowLeft className="w-5 h-5 text-slate" />
        </Button>
        <Settings className="w-8 h-8 text-slate" />
        <div>
          <h1 className="text-3xl font-display font-bold text-slate tracking-tight">
            Settings
          </h1>
          <p className="text-sm font-medium text-slate/60 mt-1">
            Manage preferences for {user?.name || user?.email}
          </p>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar */}
        <div className="w-full md:w-64 shrink-0 flex flex-col gap-2">
          <button
            onClick={() => setActiveTab('profile')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all text-left ${activeTab === 'profile' ? 'bg-slate text-vanilla flat-shadow-taupe border-2 border-slate' : 'bg-transparent text-slate hover:bg-taupe/10 border-2 border-transparent hover:border-taupe/20'}`}
          >
            <UserIcon className="w-5 h-5" />
            Profile
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all text-left ${activeTab === 'security' ? 'bg-slate text-vanilla flat-shadow-taupe border-2 border-slate' : 'bg-transparent text-slate hover:bg-taupe/10 border-2 border-transparent hover:border-taupe/20'}`}
          >
            <Shield className="w-5 h-5" />
            Security
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {activeTab === 'profile' ? (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <ProfileTab />
            </div>
          ) : (
            <SecurityTab />
          )}
        </div>
      </div>
    </div>
  )
}
