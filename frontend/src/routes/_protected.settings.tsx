import { createFileRoute, useLocation } from '@tanstack/react-router'
import { useAuth } from '#/lib/auth'
import { useState, useEffect } from 'react'
import { Lock, Save, Trash2, AlertTriangle, Pencil, Mail } from 'lucide-react'
import { api } from '#/lib/api'
import { useSessions } from '#/hooks/useSessions'
import { ScrollArea } from '#/components/ui/scroll-area'
import { Switch } from '#/components/ui/switch'
import { Button } from '#/components/ui/button'
import { Input } from '#/components/ui/input'
import { Label } from '#/components/ui/label'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '#/components/ui/card'
import { Avatar, AvatarImage, AvatarFallback } from '#/components/ui/avatar'
import { SidebarTrigger } from '#/components/ui/sidebar'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '#/components/ui/alert-dialog'

export const Route = createFileRoute('/_protected/settings')({
  component: SettingsPage,
})

function SettingsPage() {
  const { user, updateProfile } = useAuth()
  const {
    sessions,
    isLoading: isLoadingSessions,
    revokeSession,
    revokeAllSessions,
  } = useSessions()

  const [isUpdatingPreferences, setIsUpdatingPreferences] = useState(false)

  // Password State
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [passwordMessage, setPasswordMessage] = useState<{
    type: 'success' | 'error'
    text: string
  } | null>(null)

  // Profile State
  const [profileName, setProfileName] = useState('')
  const [profilePicture, setProfilePicture] = useState('')
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [isEditingPicture, setIsEditingPicture] = useState(false)
  const [profileError, setProfileError] = useState<string | null>(null)

  useEffect(() => {
    if (user) {
      setProfileName(user.name || '')
      setProfilePicture(user.picture || '')
      setIsEditingPicture(false)
    }
  }, [user])

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setProfileError(null)

    if (profilePicture && !profilePicture.startsWith('http')) {
      setProfileError(
        'Profile picture must be a valid URL starting with http/https.',
      )
      return
    }

    setIsSavingProfile(true)
    try {
      await updateProfile({ name: profileName, picture: profilePicture })
    } catch (error: any) {
      console.error('Failed to update profile', error)
      setProfileError(
        error?.response?.data?.detail || 'Failed to update profile.',
      )
    } finally {
      setIsSavingProfile(false)
    }
  }

  const location = useLocation()
  const activeTab = location.hash ? location.hash.replace('#', '') : 'profile'

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newPassword) {
      setPasswordMessage({ type: 'error', text: 'New password is required.' })
      return
    }
    if (newPassword.length < 8) {
      setPasswordMessage({
        type: 'error',
        text: 'Password must be at least 8 characters long.',
      })
      return
    }
    setIsChangingPassword(true)
    setPasswordMessage(null)
    try {
      const payload: any = { new_password: newPassword }
      if (currentPassword) payload.current_password = currentPassword
      await api.patch('/auth/password', payload)
      setPasswordMessage({
        type: 'success',
        text: 'Password successfully updated.',
      })
      setCurrentPassword('')
      setNewPassword('')
    } catch (error: any) {
      setPasswordMessage({
        type: 'error',
        text:
          error.response?.data?.detail ||
          'Failed to update password. Did you enter the correct current password?',
      })
    } finally {
      setIsChangingPassword(false)
    }
  }

  const handleDeleteAccount = async () => {
    try {
      await api.delete('/users/me')
      window.location.href = '/auth/register'
    } catch (error) {
      console.error('Failed to delete account', error)
    }
  }

  const formatSessionDate = (value: string) => {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(value))
  }

  const handleToggleReceiveUpdates = async (checked: boolean) => {
    setIsUpdatingPreferences(true)
    try {
      await updateProfile({ receive_updates: checked })
    } catch (error) {
      console.error('Failed to update preferences', error)
    } finally {
      setIsUpdatingPreferences(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-transparent">
      <header className="flex h-14 items-center gap-4 border-b border-slate-200/50 dark:border-slate-800/50 bg-white dark:bg-[#0a0a0a] px-4 shrink-0 sticky top-0 z-50">
        <SidebarTrigger />
        <h1 className="font-semibold text-lg">
          {activeTab === 'preferences'
            ? 'Preferences'
            : activeTab === 'profile'
              ? 'Profile Details'
              : activeTab === 'security'
                ? 'Security Settings'
                : 'Active Sessions'}
        </h1>
      </header>

      <ScrollArea className="flex-1 w-full">
        <main className="p-6 lg:p-8 space-y-8 max-w-3xl mx-auto">
          {activeTab === 'profile' && (
            <div className="space-y-6 animate-in fade-in duration-300">
              <Card className="relative overflow-hidden border-slate-200/60 dark:border-slate-800/60 shadow-xl dark:bg-[#121212]">
                <CardHeader>
                  <CardTitle className="text-2xl">Profile Details</CardTitle>
                  <CardDescription className="text-base">
                    Update your public profile information.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form
                    onSubmit={handleSaveProfile}
                    className="space-y-8 max-w-3xl"
                  >
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-8 mb-2">
                      <div className="relative group">
                        <Avatar className="w-28 h-28 border-4 border-white dark:border-[#121212] shadow-2xl ring-2 ring-indigo-500/20">
                          <AvatarImage
                            src={profilePicture || user?.picture || ''}
                            alt={profileName || user?.name || ''}
                          />
                          <AvatarFallback className="text-2xl bg-primary/10 text-primary">
                            {(profileName || user?.name || 'U')
                              .charAt(0)
                              .toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <button
                          type="button"
                          onClick={() => setIsEditingPicture(!isEditingPicture)}
                          className="absolute bottom-0 right-0 p-1.5 bg-black text-white dark:bg-white dark:text-black rounded-full shadow-sm hover:opacity-90 transition-opacity cursor-pointer border-2 border-background"
                          title="Edit Profile Picture"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                      </div>

                      {isEditingPicture && (
                        <div className="w-full sm:w-auto flex-1 space-y-2 animate-in fade-in slide-in-from-left-2 duration-200">
                          <Label>Profile Picture URL</Label>
                          <Input
                            type="url"
                            placeholder="https://example.com/avatar.png"
                            value={profilePicture}
                            onChange={(e) => setProfilePicture(e.target.value)}
                            autoFocus
                            className="max-w-md"
                          />
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label>Display Name</Label>
                        <Input
                          type="text"
                          placeholder="e.g. John Doe"
                          value={profileName}
                          onChange={(e) => setProfileName(e.target.value)}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Email Address</Label>
                        <Input
                          type="text"
                          disabled
                          value={user?.email || ''}
                          className="bg-muted text-muted-foreground"
                        />
                        <p className="text-xs text-muted-foreground">
                          Your email cannot be changed for security reasons.
                        </p>
                      </div>
                    </div>

                    {profileError && (
                      <p className="text-sm text-destructive font-medium">
                        {profileError}
                      </p>
                    )}

                    <Button
                      type="submit"
                      disabled={isSavingProfile}
                      className="bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-500/25 transition-all active:scale-95"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      {isSavingProfile ? 'Saving...' : 'Save Profile'}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'preferences' && (
            <div className="space-y-6 animate-in fade-in duration-300">
              <Card className="relative overflow-hidden border-slate-200/60 dark:border-slate-800/60 shadow-xl dark:bg-[#121212]">
                <CardHeader>
                  <CardTitle className="text-2xl">Email Preferences</CardTitle>
                  <CardDescription className="text-base">
                    Manage how we communicate with you via email.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between rounded-lg border p-4 w-full">
                    <div className="space-y-0.5">
                      <Label className="text-base">Email Updates</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive product updates, newsletters, and promotional
                        content.
                      </p>
                    </div>
                    <Switch
                      checked={user?.receive_updates || false}
                      onCheckedChange={handleToggleReceiveUpdates}
                      disabled={isUpdatingPreferences}
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6 animate-in fade-in duration-300">
              <Card className="relative overflow-hidden border-slate-200/60 dark:border-slate-800/60 shadow-xl dark:bg-[#121212]">
                <CardHeader>
                  <CardTitle className="text-2xl">Change Password</CardTitle>
                  <CardDescription className="text-base">
                    If you logged in with Google/GitHub and don't have a
                    password yet, leave the Current Password field blank.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleChangePassword} className="space-y-4">
                    <div className="space-y-2">
                      <Label>Current Password</Label>
                      <Input
                        type="password"
                        placeholder="Leave blank if you don't have one"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>New Password</Label>
                      <Input
                        type="password"
                        placeholder="Minimum 8 characters"
                        value={newPassword}
                        onChange={(e) => {
                          setNewPassword(e.target.value)
                          setPasswordMessage(null)
                        }}
                      />
                    </div>

                    {passwordMessage && (
                      <p
                        className={`text-sm ${passwordMessage.type === 'error' ? 'text-destructive' : 'text-emerald-500'}`}
                      >
                        {passwordMessage.text}
                      </p>
                    )}

                    <Button
                      type="submit"
                      disabled={isChangingPassword}
                      className="bg-emerald-600 text-white hover:bg-emerald-700 shadow-lg shadow-emerald-500/25 transition-all active:scale-95"
                    >
                      <Lock className="w-4 h-4 mr-2" />
                      {isChangingPassword ? 'Updating...' : 'Set Password'}
                    </Button>
                  </form>
                </CardContent>
              </Card>

              <Card className="relative overflow-hidden border-red-200/60 dark:border-red-900/40 shadow-xl shadow-red-500/5 bg-red-50 dark:bg-red-950/40">
                <CardHeader>
                  <CardTitle className="text-destructive flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" /> Danger Zone
                  </CardTitle>
                  <CardDescription className="text-destructive/80">
                    Schedule your account for deletion.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Deleting your account will immediately suspend your access
                    and hide your data. If you change your mind, you can fully
                    restore your account simply by logging back in within the
                    next 30 days. After 30 days, your data will be permanently
                    erased.
                  </p>

                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive">
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete Account
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>
                          Are you absolutely sure?
                        </AlertDialogTitle>
                        <AlertDialogDescription>
                          This action will immediately suspend your access and
                          schedule your account for permanent deletion. If you
                          change your mind, you have 30 days to cancel the
                          deletion by simply logging back in.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={handleDeleteAccount}
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                          Yes, delete my account
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'sessions' && (
            <div className="space-y-6 animate-in fade-in duration-300">
              <Card className="border-slate-200/60 dark:border-slate-800/60 shadow-xl dark:bg-[#121212]">
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle>Active Sessions</CardTitle>
                    <CardDescription>
                      Manage the devices currently logged into your account.
                    </CardDescription>
                  </div>
                  {sessions.length > 1 && (
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="destructive" size="sm">
                          Log out of all devices
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>
                            Revoke All Sessions
                          </AlertDialogTitle>
                          <AlertDialogDescription>
                            This will log you out of all other devices
                            immediately. You will remain logged in on this
                            device.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => revokeAllSessions.mutate()}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                          >
                            Yes, revoke all
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  )}
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {isLoadingSessions && (
                      <div className="text-sm text-muted-foreground">
                        Loading sessions...
                      </div>
                    )}

                    {!isLoadingSessions && sessions.length === 0 && (
                      <div className="text-sm text-muted-foreground">
                        No active sessions found.
                      </div>
                    )}

                    {sessions.map((session) => (
                      <div
                        key={session.family_id}
                        className="flex items-center justify-between gap-4 p-4 border rounded-lg bg-card"
                      >
                        <div className="min-w-0 flex items-start gap-4">
                          {session.auth_provider === 'google' ? (
                            <svg
                              className="w-5 h-5 mt-1 text-muted-foreground shrink-0"
                              viewBox="0 0 24 24"
                            >
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
                          ) : session.auth_provider === 'github' ? (
                            <svg
                              className="w-5 h-5 mt-1 text-muted-foreground shrink-0"
                              fill="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                fillRule="evenodd"
                                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                                clipRule="evenodd"
                              />
                            </svg>
                          ) : (
                            <Mail className="w-5 h-5 mt-1 text-muted-foreground shrink-0" />
                          )}
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">
                              {session.user_agent || 'Unknown device'}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1 flex items-center gap-2">
                              <span>{session.ip_address || 'Unknown IP'}</span>
                              <span>&bull;</span>
                              <span>
                                Last active{' '}
                                {formatSessionDate(session.last_active)}
                              </span>
                              <span>&bull;</span>
                              <span className="capitalize">
                                {session.auth_provider === 'local'
                                  ? 'Email / Password'
                                  : session.auth_provider}
                              </span>
                            </p>
                          </div>
                        </div>
                        {session.is_current ? (
                          <span className="shrink-0 text-xs font-medium text-emerald-600 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20">
                            Current
                          </span>
                        ) : (
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                variant="outline"
                                size="sm"
                                className="shrink-0 text-destructive border-destructive/20 hover:bg-destructive/10"
                              >
                                Revoke
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>
                                  Revoke Session
                                </AlertDialogTitle>
                                <AlertDialogDescription>
                                  This will immediately log out the device. It
                                  will need to log in again to access the
                                  account.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() =>
                                    revokeSession.mutate(session.family_id)
                                  }
                                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                >
                                  Yes, revoke
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </ScrollArea>
    </div>
  )
}
