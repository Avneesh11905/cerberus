import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { RefreshCw, Plus, Shield, Trash2, AlertTriangle } from 'lucide-react'
import { toast } from 'sonner'
import { extractErrorMessage } from '../lib/api-client'
import { useProject } from '../contexts/ProjectContext'
import { updateProjectOAuth } from '../api/projects'
import { API_URL } from '../lib/api-client'
import { CopyButton } from '../components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select'

export const Route = createFileRoute('/_protected/projects/$projectId/auth')({
  component: AuthTab,
})

function AuthTab() {
  const { projectId } = Route.useParams()
  const { project, fetchProject } = useProject()

  const [allowedProviders, setAllowedProviders] = useState<string[]>([])
  const [githubClientId, setGithubClientId] = useState('')
  const [githubClientSecret, setGithubClientSecret] = useState('')
  const [googleClientId, setGoogleClientId] = useState('')
  const [googleClientSecret, setGoogleClientSecret] = useState('')
  const [savingAuth, setSavingAuth] = useState(false)
  const [authErrors, setAuthErrors] = useState<Record<string, string>>({})

  const [isProviderModalOpen, setIsProviderModalOpen] = useState(false)
  const [editingProvider, setEditingProvider] = useState<string | null>(null)
  const [modalProvider, setModalProvider] = useState('')
  const [modalClientId, setModalClientId] = useState('')
  const [modalClientSecret, setModalClientSecret] = useState('')
  const [providerToDelete, setProviderToDelete] = useState<string | null>(null)

  useEffect(() => {
    if (project) {
      const providers: string[] = []
      if (project.oauth_config?.github?.enabled) {
        providers.push('github')
        setGithubClientId(project.oauth_config.github.client_id || '')
      }
      if (project.oauth_config?.google?.enabled) {
        providers.push('google')
        setGoogleClientId(project.oauth_config.google.client_id || '')
      }
      setAllowedProviders(providers)
    }
  }, [project])

  const openAddProviderModal = () => {
    setEditingProvider(null)
    setModalProvider('')
    setModalClientId('')
    setModalClientSecret('')
    setIsProviderModalOpen(true)
  }

  const openEditProviderModal = (provider: string) => {
    setEditingProvider(provider)
    setModalProvider(provider)
    if (provider === 'github') {
      setModalClientId(githubClientId)
      setModalClientSecret(githubClientSecret)
    } else if (provider === 'google') {
      setModalClientId(googleClientId)
      setModalClientSecret(googleClientSecret)
    }
    setIsProviderModalOpen(true)
  }

  const handleModalSave = async () => {
    if (!modalProvider) {
      setAuthErrors({ provider: 'Please select a provider' })
      return
    }

    setSavingAuth(true)
    setAuthErrors({})

    const newAllowedProviders = allowedProviders.includes(modalProvider)
      ? allowedProviders
      : [...allowedProviders, modalProvider]

    const newGithubClientId =
      modalProvider === 'github' ? modalClientId : githubClientId
    const newGithubClientSecret =
      modalProvider === 'github' ? modalClientSecret : githubClientSecret
    const newGoogleClientId =
      modalProvider === 'google' ? modalClientId : googleClientId
    const newGoogleClientSecret =
      modalProvider === 'google' ? modalClientSecret : googleClientSecret

    try {
      await updateProjectOAuth(projectId, {
        oauth_config: {
          github: {
            enabled: newAllowedProviders.includes('github'),
            client_id: newGithubClientId || undefined,
            client_secret: newGithubClientSecret || undefined,
          },
          google: {
            enabled: newAllowedProviders.includes('google'),
            client_id: newGoogleClientId || undefined,
            client_secret: newGoogleClientSecret || undefined,
          },
        },
      })

      setAllowedProviders(newAllowedProviders)
      if (modalProvider === 'github') {
        setGithubClientId(newGithubClientId)
        setGithubClientSecret('')
      } else if (modalProvider === 'google') {
        setGoogleClientId(newGoogleClientId)
        setGoogleClientSecret('')
      }
      setIsProviderModalOpen(false)
      fetchProject(false)
    } catch (error: unknown) {
      if (
        axios.isAxiosError(error) &&
        error.response?.status === 422 &&
        Array.isArray(error.response?.data?.detail)
      ) {
        const errors: Record<string, string> = {}
        error.response.data.detail.forEach((d: any) => {
          if (d.loc.length >= 4 && d.loc[1] === 'oauth_config') {
            const provider = d.loc[2]
            const field = d.loc[3]
            errors[`${provider}_${field}`] = d.msg
          } else {
            const field = d.loc[d.loc.length - 1]
            errors[field] = d.msg
          }
        })
        setAuthErrors(errors)
      } else {
        toast.error(
          extractErrorMessage(error, 'Failed to update auth settings'),
        )
      }
    } finally {
      setSavingAuth(false)
    }
  }

  const removeProvider = async () => {
    if (!providerToDelete) return
    setSavingAuth(true)

    const newAllowedProviders = allowedProviders.filter(
      (p) => p !== providerToDelete,
    )

    let ghId: string | null | undefined = githubClientId || undefined
    let ghSecret: string | null | undefined = githubClientSecret || undefined
    let ggId: string | null | undefined = googleClientId || undefined
    let ggSecret: string | null | undefined = googleClientSecret || undefined

    if (providerToDelete === 'github') {
      ghId = null
      ghSecret = null
    } else if (providerToDelete === 'google') {
      ggId = null
      ggSecret = null
    }

    try {
      await updateProjectOAuth(projectId, {
        oauth_config: {
          github: {
            enabled: newAllowedProviders.includes('github'),
            client_id: ghId,
            client_secret: ghSecret,
          },
          google: {
            enabled: newAllowedProviders.includes('google'),
            client_id: ggId,
            client_secret: ggSecret,
          },
        },
      })

      setAllowedProviders(newAllowedProviders)
      if (providerToDelete === 'github') {
        setGithubClientId('')
        setGithubClientSecret('')
      } else if (providerToDelete === 'google') {
        setGoogleClientId('')
        setGoogleClientSecret('')
      }
      setProviderToDelete(null)
      fetchProject(false)
    } catch (error: unknown) {
      toast.error(extractErrorMessage(error, 'Failed to save provider'))
    } finally {
      setSavingAuth(false)
    }
  }

  return (
    <div className="flex flex-col gap-8 w-full animate-in fade-in slide-in-from-bottom-2 duration-300">
      <Card>
        <CardHeader className="flex flex-row items-start justify-between space-y-0">
          <div className="space-y-1.5">
            <CardTitle>OAuth Providers</CardTitle>
            <CardDescription>
              Configure third-party social logins for your project.
            </CardDescription>
          </div>
          <Button
            type="button"
            onClick={openAddProviderModal}
            className="gap-2"
          >
            <Plus className="w-4 h-4" /> Add Provider
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          {allowedProviders.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-taupe bg-taupe/5 rounded-xl">
              <Shield className="w-12 h-12 text-taupe mb-4" />
              <h3 className="text-lg font-bold text-slate mb-2">
                No Providers Configured
              </h3>
              <p className="text-sm font-semibold text-slate/70 text-center max-w-md">
                You haven't added any social login providers yet. Add a
                provider to allow your users to sign in with their
                existing accounts.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {allowedProviders.map((provider) => (
                <div
                  key={provider}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-5 border-2 border-slate rounded-xl bg-vanilla shadow-[4px_4px_0px_rgba(30,41,59,1)] gap-4"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <h4 className="text-lg font-black text-slate capitalize">
                        {provider} Login
                      </h4>
                      <p className="text-sm font-semibold text-slate/70">
                        Users can sign in with their{' '}
                        {provider.charAt(0).toUpperCase() +
                          provider.slice(1)}{' '}
                        accounts.
                      </p>
                    </div>

                    <div className="flex flex-col gap-1 mt-3 p-3 bg-taupe/10 border-2 border-slate/10 rounded-xl">
                      <span className="text-xs font-bold text-slate/70 uppercase">
                        Callback URL
                      </span>
                      <div className="flex items-center gap-2">
                        <code className="flex-1 text-xs font-mono bg-vanilla px-2 py-1.5 rounded-lg border border-slate/10 break-all">
                          {`${API_URL}/auth/callback/${provider}`}
                        </code>
                        <CopyButton
                          value={`${API_URL}/auth/callback/${provider}`}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => openEditProviderModal(provider)}
                    >
                      Edit
                    </Button>
                    <Button
                      type="button"
                      variant="destructive"
                      size="sm"
                      onClick={() => setProviderToDelete(provider)}
                      disabled={savingAuth}
                    >
                      {savingAuth && providerToDelete === provider ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* PROVIDER MODAL */}
      <Dialog open={isProviderModalOpen} onOpenChange={setIsProviderModalOpen}>
        <DialogContent className="sm:max-w-106.25 border-2 border-slate bg-vanilla p-0 overflow-hidden shadow-[8px_8px_0px_rgba(30,41,59,1)]">
          <DialogHeader className="p-6 bg-sand border-b-2 border-slate">
            <DialogTitle className="text-2xl font-black text-slate">
              {editingProvider
                ? `Edit ${editingProvider.charAt(0).toUpperCase() + editingProvider.slice(1)}`
                : 'Add Provider'}
            </DialogTitle>
            <DialogDescription className="font-semibold text-slate/70">
              {editingProvider
                ? 'Update the OAuth credentials.'
                : 'Select a provider and enter the credentials to enable social login.'}
            </DialogDescription>
          </DialogHeader>
          <div className="p-6 space-y-4">
            {!editingProvider && (
              <div className="space-y-2">
                <Label>Provider</Label>
                <Select
                  value={modalProvider}
                  onValueChange={(val) => {
                    setModalProvider(val)
                    setAuthErrors({ ...authErrors, provider: '' })
                  }}
                >
                  <SelectTrigger
                    className={
                      authErrors.provider
                        ? 'border-terracotta focus:ring-terracotta'
                        : ''
                    }
                  >
                    <SelectValue placeholder="Select a provider" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem
                      value="github"
                      disabled={allowedProviders.includes('github')}
                    >
                      GitHub
                    </SelectItem>
                    <SelectItem
                      value="google"
                      disabled={allowedProviders.includes('google')}
                    >
                      Google
                    </SelectItem>
                  </SelectContent>
                </Select>
                {authErrors.provider && (
                  <p className="text-sm font-bold text-terracotta">
                    {authErrors.provider}
                  </p>
                )}
              </div>
            )}

            {modalProvider && (
              <div className="space-y-2 pb-2 mb-2 border-b-2 border-slate/10">
                <Label>Callback URL</Label>
                <div className="flex items-center justify-between gap-2 p-2 bg-taupe/10 border-2 border-slate/20 rounded-xl">
                  <code className="text-xs font-mono truncate max-w-70">
                    {`${API_URL}/auth/callback/${modalProvider}`}
                  </code>
                  <CopyButton
                    value={`${API_URL}/auth/callback/${modalProvider}`}
                  />
                </div>
                <p className="text-xs font-semibold text-slate/60">
                  Set this as the Authorized Redirect URI in your{' '}
                  {modalProvider.charAt(0).toUpperCase() +
                    modalProvider.slice(1)}{' '}
                  console.
                </p>
              </div>
            )}

            <div className="space-y-2">
              <Label>Client ID</Label>
              <Input
                value={modalClientId}
                onChange={(e) => {
                  setModalClientId(e.target.value)
                  if (modalProvider) {
                    setAuthErrors({
                      ...authErrors,
                      [`${modalProvider}_client_id`]: '',
                    })
                  }
                }}
                placeholder="Client ID"
                className={
                  authErrors[`${modalProvider}_client_id`]
                    ? 'border-terracotta focus-visible:ring-terracotta'
                    : ''
                }
              />
              {authErrors[`${modalProvider}_client_id`] && (
                <p className="text-sm font-bold text-terracotta">
                  {authErrors[`${modalProvider}_client_id`]}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Client Secret</Label>
              <Input
                type="password"
                value={modalClientSecret}
                onChange={(e) => {
                  setModalClientSecret(e.target.value)
                  if (modalProvider) {
                    setAuthErrors({
                      ...authErrors,
                      [`${modalProvider}_client_secret`]: '',
                    })
                  }
                }}
                placeholder="Client Secret"
                className={
                  authErrors[`${modalProvider}_client_secret`]
                    ? 'border-terracotta focus-visible:ring-terracotta'
                    : ''
                }
              />
              {authErrors[`${modalProvider}_client_secret`] && (
                <p className="text-sm font-bold text-terracotta">
                  {authErrors[`${modalProvider}_client_secret`]}
                </p>
              )}
            </div>
          </div>
          <DialogFooter className="p-6 bg-sand border-t-2 border-slate flex justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsProviderModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handleModalSave}
              disabled={savingAuth}
            >
              {savingAuth ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : editingProvider ? (
                'Save Changes'
              ) : (
                'Add Provider'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* DELETE CONFIRMATION MODALS */}
      <Dialog
        open={!!providerToDelete}
        onOpenChange={(open) => !open && setProviderToDelete(null)}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl font-black text-terracotta flex items-center gap-2">
              <AlertTriangle className="w-6 h-6" /> Remove Provider?
            </DialogTitle>
            <DialogDescription className="text-slate/80 font-semibold pt-4">
              Are you sure you want to remove the{' '}
              <strong className="capitalize">{providerToDelete}</strong>{' '}
              provider? Users relying on this provider will no longer be able to
              log in.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-6 flex justify-end gap-2">
            <Button variant="outline" onClick={() => setProviderToDelete(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={removeProvider}
              disabled={savingAuth}
            >
              {savingAuth ? (
                <RefreshCw className="w-4 h-4 animate-spin mr-2" />
              ) : null}
              Remove
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
