import { createFileRoute, useLocation, Link } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import {
  useOAuthProviders,
  useProjects,
  useProjectSecrets,
} from '#/hooks/useProjects'
import type { OAuthConfig } from '#/hooks/useProjects'
import { SecretRevealModal } from '#/components/SecretRevealModal'
import type { SecretRevealMode } from '#/components/SecretRevealModal'
import {
  Trash2,
  Eye,
  EyeOff,
  Plus,
  X,
  Copy,
  Check,
  Info,
  Mail,
  Globe,
  Shield,
  Code2,
  Github,
} from 'lucide-react'
import { Skeleton } from '#/components/ui/skeleton'
import { Label } from '#/components/ui/label'
import { ScrollArea, ScrollBar } from '#/components/ui/scroll-area'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '#/components/ui/alert-dialog'
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from '#/components/ui/context-menu'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from '#/components/ui/tooltip'
import { SidebarTrigger } from '#/components/ui/sidebar'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '#/components/ui/card'
import { Button } from '#/components/ui/button'
import { Input } from '#/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '#/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '#/components/ui/select'

export const Route = createFileRoute('/_protected/projects/$projectId')({
  component: ProjectConfig,
})

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={handleCopy}
      className="h-8 w-8 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white bg-slate-100 dark:bg-slate-800 transition-colors"
    >
      {copied ? (
        <Check className="w-4 h-4 text-emerald-500" />
      ) : (
        <Copy className="w-4 h-4" />
      )}
    </Button>
  )
}

function ProjectConfig() {
  const { projectId } = Route.useParams()
  const {
    projects,
    isLoading,
    updateProjectOauth,
    updateProjectOrigins,
    updateProjectEnvironment,
    updateProjectName,
    updateProjectFrontendUrl,
    rotateApiKey,
    rotateJwtSecret,
    deleteProject,
  } = useProjects()
  const { data: oauthProviders = [] } = useOAuthProviders()
  const project = projects.find((p) => p.id === projectId)

  const location = useLocation()
  const activeTab = location.hash ? location.hash.replace('#', '') : 'general'

  const [editName, setEditName] = useState('')

  // Modals
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [isRotateApiModalOpen, setIsRotateApiModalOpen] = useState(false)
  const [isRotateJwtModalOpen, setIsRotateJwtModalOpen] = useState(false)
  const [isAddProviderModalOpen, setIsAddProviderModalOpen] = useState(false)
  const [deleteConfirmName, setDeleteConfirmName] = useState('')
  const [showJwt, setShowJwt] = useState(false)

  useEffect(() => {
    if (project?.name) setEditName(project.name)
  }, [project?.name])

  const handleSaveName = async () => {
    if (!editName.trim() || editName.trim() === project?.name) {
      return
    }
    await updateProjectName.mutateAsync({ projectId, name: editName.trim() })
  }

  const [frontendUrl, setFrontendUrl] = useState('')
  const [frontendUrlError, setFrontendUrlError] = useState<string | null>(null)

  useEffect(() => {
    if (project?.frontend_url) setFrontendUrl(project.frontend_url)
    else setFrontendUrl('')
  }, [project?.frontend_url])

  const isValidUrl = (urlString: string) => {
    try {
      const url = new URL(urlString)
      return url.protocol === 'http:' || url.protocol === 'https:'
    } catch (e) {
      return false
    }
  }

  const handleSaveFrontendUrl = async () => {
    setFrontendUrlError(null)
    const val = frontendUrl.trim()
    if (!val) return
    if (!isValidUrl(val)) {
      setFrontendUrlError(
        'Please enter a valid URL starting with http:// or https://',
      )
      return
    }
    await updateProjectFrontendUrl.mutateAsync({ projectId, frontend_url: val })
  }

  const [oauthConfig, setOauthConfig] = useState<OAuthConfig>({
    local: { enabled: true },
  })

  useEffect(() => {
    const nextConfig: OAuthConfig = {
      local: project?.oauth_config?.local || { enabled: true },
    }
    for (const provider of oauthProviders) {
      nextConfig[provider.key] = project?.oauth_config?.[provider.key] || {
        enabled: false,
        client_id: '',
        client_secret: '',
      }
    }
    if (project?.oauth_config) {
      for (const [provider, config] of Object.entries(project.oauth_config)) {
        nextConfig[provider] = config
      }
    }
    setOauthConfig(nextConfig)
  }, [oauthProviders, project?.oauth_config])

  const [allowedOrigins, setAllowedOrigins] = useState<string[]>([])
  const [newOrigin, setNewOrigin] = useState('')
  const [originError, setOriginError] = useState<string | null>(null)

  useEffect(() => {
    if (project?.allowed_origins) {
      setAllowedOrigins(project.allowed_origins)
    }
  }, [project?.allowed_origins])

  const [revealSecrets, setRevealSecrets] = useState<{
    api_key?: string
    public_key?: string
  } | null>(null)
  const [revealMode, setRevealMode] =
    useState<SecretRevealMode>('api_key_rotated')
  const { data: secrets } = useProjectSecrets(projectId)

  if (isLoading) {
    return (
      <div className="space-y-8 max-w-6xl mx-auto">
        <div className="flex items-center gap-4">
          <Skeleton className="w-9 h-9 rounded-full" />
          <div>
            <Skeleton className="w-64 h-9 mb-2" />
            <Skeleton className="w-48 h-5" />
          </div>
        </div>
        <Skeleton className="w-full h-96 rounded-xl" />
      </div>
    )
  }

  if (!project)
    return (
      <div className="text-slate-900 dark:text-white">Project not found</div>
    )

  const saveOauthConfig = async (newConfig: OAuthConfig) => {
    setOauthConfig(newConfig)
    await updateProjectOauth.mutateAsync({
      projectId,
      oauth_config: newConfig,
    })
    setIsAddProviderModalOpen(false)
  }

  const handleProviderSave = async (
    provider: string,
    client_id: string,
    client_secret: string,
  ) => {
    const newConfig = {
      ...oauthConfig,
      [provider]: {
        enabled: true,
        client_id,
        ...(client_secret ? { client_secret } : {}),
      },
    }
    saveOauthConfig(newConfig)
  }

  const handleProviderDisable = async (provider: string) => {
    const newConfig = {
      ...oauthConfig,
      [provider]: { enabled: false, client_id: '', client_secret: '' },
    }
    saveOauthConfig(newConfig)
  }

  const handleAddOrigin = async () => {
    setOriginError(null)
    const cleanOrigin = newOrigin.trim().replace(/\/$/, '')
    if (!cleanOrigin) return

    if (!isValidUrl(cleanOrigin)) {
      setOriginError(
        'Please enter a valid URL starting with http:// or https://',
      )
      return
    }

    if (cleanOrigin && !allowedOrigins.includes(cleanOrigin)) {
      if (allowedOrigins.length >= 5) {
        alert('Maximum 5 origins allowed per project.')
        return
      }
      const newOrigins = [...allowedOrigins, cleanOrigin]
      setAllowedOrigins(newOrigins)
      setNewOrigin('')
      await updateProjectOrigins.mutateAsync({
        projectId,
        allowed_origins: newOrigins,
      })
    }
  }

  const handleRemoveOrigin = async (origin: string) => {
    const newOrigins = allowedOrigins.filter((o) => o !== origin)
    setAllowedOrigins(newOrigins)
    await updateProjectOrigins.mutateAsync({
      projectId,
      allowed_origins: newOrigins,
    })
  }

  const handleToggleEnvironment = async () => {
    const newEnv =
      project.environment === 'development' ? 'production' : 'development'
    await updateProjectEnvironment.mutateAsync({
      projectId,
      environment: newEnv,
    })
  }

  const doRotateApiKey = async () => {
    const res = await rotateApiKey.mutateAsync(projectId)
    setRevealMode('api_key_rotated')
    setRevealSecrets({ api_key: res.api_key })
    setIsRotateApiModalOpen(false)
  }

  const doRotateJwtSecret = async () => {
    const res = await rotateJwtSecret.mutateAsync(projectId)
    setRevealMode('jwt_rotated')
    setRevealSecrets({ public_key: res.public_key })
    setIsRotateJwtModalOpen(false)
  }

  const doDeleteProject = async () => {
    await deleteProject.mutateAsync(projectId)
    window.location.href = '/dashboard'
  }

  const enabledProviders = oauthProviders.filter(
    (p) => oauthConfig[p.key].enabled,
  )
  const disabledProviders = oauthProviders.filter(
    (p) => !oauthConfig[p.key].enabled,
  )

  const AddProviderModal = () => {
    if (!isAddProviderModalOpen) return null
    const [selectedProvider, setSelectedProvider] = useState(
      disabledProviders[0]?.key || '',
    )
    const [clientId, setClientId] = useState('')
    const [clientSecret, setClientSecret] = useState('')

    if (disabledProviders.length === 0) {
      return (
        <Dialog
          open={isAddProviderModalOpen}
          onOpenChange={setIsAddProviderModalOpen}
        >
          <DialogContent className="sm:max-w-md text-center py-8">
            <p className="text-foreground font-medium mb-4">
              All available providers are already enabled.
            </p>
            <Button
              variant="outline"
              onClick={() => setIsAddProviderModalOpen(false)}
            >
              Close
            </Button>
          </DialogContent>
        </Dialog>
      )
    }

    return (
      <Dialog
        open={isAddProviderModalOpen}
        onOpenChange={setIsAddProviderModalOpen}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add Identity Provider</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <div className="space-y-2">
              <Label>Select Provider</Label>
              <Select
                value={selectedProvider}
                onValueChange={setSelectedProvider}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select provider" />
                </SelectTrigger>
                <SelectContent>
                  {disabledProviders.map((p) => (
                    <SelectItem key={p.key} value={p.key}>
                      <div className="flex items-center gap-2">
                        {p.key === 'github' ? (
                          <svg
                            viewBox="0 0 24 24"
                            className="w-4 h-4 fill-current"
                          >
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                          </svg>
                        ) : p.key === 'google' ? (
                          <svg viewBox="0 0 24 24" className="w-4 h-4">
                            <path
                              fill="#4285F4"
                              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            />
                            <path
                              fill="#34A853"
                              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            />
                            <path
                              fill="#FBBC05"
                              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                            />
                            <path
                              fill="#EA4335"
                              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            />
                          </svg>
                        ) : null}
                        {p.display_name}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Client ID</Label>
              <Input
                type="text"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Client Secret</Label>
              <Input
                type="password"
                value={clientSecret}
                onChange={(e) => setClientSecret(e.target.value)}
              />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button
              variant="outline"
              onClick={() => setIsAddProviderModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={() =>
                handleProviderSave(selectedProvider, clientId, clientSecret)
              }
              disabled={!clientId || !clientSecret}
            >
              Add Provider
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <TooltipProvider>
      <div className="w-full h-full flex flex-col flex-1 min-h-0 bg-transparent">
        <header className="flex h-14 items-center gap-4 border-b border-slate-200/50 dark:border-slate-800/50 backdrop-blur-md bg-white/70 dark:bg-[#0a0a0a]/70 px-4 shrink-0 sticky top-0 z-50">
          <SidebarTrigger />
          <h1 className="font-semibold text-lg">
            {activeTab === 'general' && 'General Settings'}
            {activeTab === 'providers' && 'Identity Providers'}
            {activeTab === 'origins' && 'Origins & CORS'}
            {activeTab === 'keys' && 'Access Keys & Secrets'}
          </h1>
          <div className="flex-1" />
          <div className="flex items-center gap-4 text-sm font-medium">
            <Link
              to="/docs/sdk"
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <Code2 className="w-4 h-4" />
              <span className="hidden sm:inline">SDK Docs</span>
            </Link>
            <a
              href="https://github.com/Avneesh11905/cerberus"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <Github className="w-4 h-4" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          <div className="max-w-4xl mx-auto">
            {activeTab === 'general' && (
              <div className="space-y-6 animate-in fade-in duration-300">
                <Card>
                  <CardHeader>
                    <CardTitle>Project Details</CardTitle>
                    <CardDescription>
                      Manage your project's identity and environment settings.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <Label>Project Name</Label>
                      <div className="flex gap-2 max-w-xl">
                        <Input
                          type="text"
                          value={editName}
                          onChange={(e) => setEditName(e.target.value)}
                          onKeyDown={(e) =>
                            e.key === 'Enter' && handleSaveName()
                          }
                          className="flex-1"
                        />
                        <Button
                          onClick={handleSaveName}
                          disabled={
                            updateProjectName.isPending ||
                            editName === project.name
                          }
                        >
                          Save
                        </Button>
                      </div>
                    </div>

                    <div className="pt-6 border-t border-border space-y-4">
                      <div>
                        <h3 className="text-sm font-medium text-foreground flex items-center gap-1.5 mb-1">
                          Environment
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Info className="w-4 h-4 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>
                                Production environments have stricter rate
                                limits and security policies.
                              </p>
                            </TooltipContent>
                          </Tooltip>
                        </h3>
                        <p className="text-sm text-muted-foreground mb-4">
                          Toggle between development mode and production mode.
                        </p>
                      </div>
                      <Button
                        variant={
                          project.environment === 'development'
                            ? 'default'
                            : 'secondary'
                        }
                        onClick={handleToggleEnvironment}
                        disabled={updateProjectEnvironment.isPending}
                        className={
                          project.environment === 'development'
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20 shadow-none'
                            : 'bg-amber-500/10 text-amber-600 dark:text-amber-500 hover:bg-amber-500/20 border border-amber-500/20 shadow-none'
                        }
                      >
                        Switch to{' '}
                        {project.environment === 'development'
                          ? 'Production'
                          : 'Development'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-red-200 dark:border-red-900/50 bg-red-50/50 dark:bg-red-900/10">
                  <CardHeader>
                    <CardTitle className="text-red-600 dark:text-red-500">
                      Danger Zone
                    </CardTitle>
                    <CardDescription className="text-red-600/80 dark:text-red-400/80">
                      Irreversible destructive actions.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div>
                        <h4 className="font-medium text-slate-900 dark:text-white">
                          Delete Project
                        </h4>
                        <p className="text-sm text-red-600/80 dark:text-red-400/80 mt-1">
                          Permanently delete this project and all its users.
                        </p>
                      </div>
                      <Button
                        variant="destructive"
                        onClick={() => setIsDeleteModalOpen(true)}
                        disabled={deleteProject.isPending}
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete Project
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === 'providers' && (
              <div className="space-y-6 animate-in fade-in duration-300">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle>Identity Providers</CardTitle>
                      <CardDescription>
                        Configure which authentication methods your users can
                        use.
                      </CardDescription>
                    </div>
                    <Button onClick={() => setIsAddProviderModalOpen(true)}>
                      <Plus className="w-4 h-4 mr-2" />
                      Add Provider
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-5 border border-border rounded-xl bg-slate-50/50 dark:bg-slate-900/20 transition-colors">
                        <div className="flex items-center gap-4">
                          <div className="p-3 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg">
                            <Mail className="w-6 h-6" />
                          </div>
                          <div>
                            <h3 className="font-medium text-foreground">
                              Email & Password
                            </h3>
                            <p className="text-sm text-muted-foreground mt-1">
                              Standard local authentication.
                            </p>
                          </div>
                        </div>
                        <div className="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs font-medium rounded-full cursor-not-allowed">
                          Required
                        </div>
                      </div>

                      {enabledProviders.map((provider) => {
                        return (
                          <div
                            key={provider.key}
                            className="flex items-center justify-between p-5 border border-border rounded-xl bg-card hover:bg-accent/50 transition-colors"
                          >
                            <div className="flex items-center gap-4">
                              <div className="p-3 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg">
                                {provider.key === 'github' ? (
                                  <svg
                                    viewBox="0 0 24 24"
                                    className="w-6 h-6 fill-current"
                                  >
                                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                                  </svg>
                                ) : provider.key === 'google' ? (
                                  <svg viewBox="0 0 24 24" className="w-6 h-6">
                                    <path
                                      fill="#4285F4"
                                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                    />
                                    <path
                                      fill="#34A853"
                                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                    />
                                    <path
                                      fill="#FBBC05"
                                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                    />
                                    <path
                                      fill="#EA4335"
                                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                    />
                                  </svg>
                                ) : (
                                  <div className="w-6 h-6 rounded-full bg-slate-300 dark:bg-slate-700" />
                                )}
                              </div>
                              <div>
                                <h3 className="font-medium text-foreground">
                                  {provider.display_name}
                                </h3>
                                <p className="text-sm text-muted-foreground mt-1">
                                  OAuth integration is active.
                                </p>
                              </div>
                            </div>
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() =>
                                handleProviderDisable(provider.key)
                              }
                            >
                              Remove
                            </Button>
                          </div>
                        )
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === 'origins' && (
              <div className="space-y-8 animate-in fade-in duration-300">
                <Card>
                  <CardHeader className="flex flex-row items-start gap-4 space-y-0">
                    <div className="p-2.5 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg shrink-0 mt-1">
                      <Globe className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-lg">
                        Frontend App URL
                      </CardTitle>
                      <CardDescription className="mt-1.5">
                        This is the primary URL where your frontend application
                        is hosted. We use this to redirect your users back to
                        your app after they successfully log in via OAuth
                        providers.
                      </CardDescription>
                    </div>
                  </CardHeader>
                  <CardContent className="pl-18">
                    <div className="flex flex-col sm:flex-row gap-3 max-w-2xl">
                      <Input
                        type="url"
                        placeholder="e.g. https://my-app.com"
                        value={frontendUrl}
                        onChange={(e) => setFrontendUrl(e.target.value)}
                        onKeyDown={(e) =>
                          e.key === 'Enter' && handleSaveFrontendUrl()
                        }
                        className="flex-1"
                      />
                      <Button
                        onClick={handleSaveFrontendUrl}
                        disabled={
                          updateProjectFrontendUrl.isPending ||
                          frontendUrl.trim() === project.frontend_url
                        }
                        className="shrink-0"
                      >
                        Save Changes
                      </Button>
                    </div>
                    {frontendUrlError && (
                      <p className="text-sm text-destructive font-medium mt-2">
                        {frontendUrlError}
                      </p>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-start gap-4 space-y-0">
                    <div className="p-2.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg shrink-0 mt-1">
                      <Shield className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-lg">
                        Allowed CORS Origins
                      </CardTitle>
                      <CardDescription className="mt-1.5">
                        Whitelist specific domains that are permitted to make
                        API requests to your Cerberus project. Requests from
                        domains not listed here will be blocked by the browser.
                        You can add up to 5 origins.
                      </CardDescription>
                    </div>
                  </CardHeader>
                  <CardContent className="pl-18 space-y-6">
                    <div className="flex flex-col sm:flex-row gap-3 max-w-2xl">
                      <Input
                        type="text"
                        placeholder="e.g. https://admin.my-app.com"
                        value={newOrigin}
                        onChange={(e) => setNewOrigin(e.target.value)}
                        onKeyDown={(e) =>
                          e.key === 'Enter' && handleAddOrigin()
                        }
                        className="flex-1"
                      />
                      <Button
                        onClick={handleAddOrigin}
                        variant="secondary"
                        disabled={
                          allowedOrigins.length >= 5 || !newOrigin.trim()
                        }
                        className="shrink-0"
                      >
                        Add Origin
                      </Button>
                    </div>
                    {originError && (
                      <p className="text-sm text-destructive font-medium mt-2">
                        {originError}
                      </p>
                    )}

                    {allowedOrigins.length > 0 ? (
                      <div className="max-w-2xl border border-border rounded-lg overflow-hidden">
                        <ul className="divide-y divide-border">
                          {allowedOrigins.map((origin) => (
                            <ContextMenu key={origin}>
                              <ContextMenuTrigger>
                                <li className="flex items-center justify-between p-3.5 bg-card hover:bg-muted/30 transition-colors">
                                  <span className="text-sm font-mono cursor-default text-foreground/90">
                                    {origin}
                                  </span>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => handleRemoveOrigin(origin)}
                                    className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                                  >
                                    <X className="w-4 h-4" />
                                  </Button>
                                </li>
                              </ContextMenuTrigger>
                              <ContextMenuContent>
                                <ContextMenuItem
                                  onClick={() => {
                                    navigator.clipboard.writeText(origin)
                                  }}
                                >
                                  <Copy className="mr-2 h-4 w-4" />
                                  Copy Origin
                                </ContextMenuItem>
                                <ContextMenuItem
                                  onClick={() => handleRemoveOrigin(origin)}
                                  className="text-destructive focus:bg-destructive/10 focus:text-destructive"
                                >
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  Remove
                                </ContextMenuItem>
                              </ContextMenuContent>
                            </ContextMenu>
                          ))}
                        </ul>
                      </div>
                    ) : (
                      <div className="p-8 border border-dashed border-border rounded-xl text-center max-w-2xl bg-muted/20">
                        <Shield className="w-8 h-8 mx-auto mb-3 text-muted-foreground/50" />
                        <p className="text-sm font-medium text-foreground">
                          No origins whitelisted
                        </p>
                        <p className="text-sm text-muted-foreground mt-1">
                          External API requests from browsers will be blocked
                          until you add an origin.
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === 'keys' && (
              <div className="space-y-6 animate-in fade-in duration-300">
                {/* API Key Card */}
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle>Project API Key</CardTitle>
                      <CardDescription>
                        Used to scope SDK requests to this project via{' '}
                        <code className="text-xs bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">
                          X-Cerberus-API-Key
                        </code>
                      </CardDescription>
                    </div>
                    <Button
                      onClick={() => setIsRotateApiModalOpen(true)}
                      variant="outline"
                      size="sm"
                      className="h-7 px-3 text-xs font-medium bg-amber-500/10 text-amber-700 dark:text-amber-500 hover:bg-amber-500/20 border-amber-500/20 transition-colors"
                    >
                      Rotate Key
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {/* Masked key display */}
                      <div className="flex items-center gap-2 p-3 bg-slate-50 dark:bg-black/40 border border-slate-200 dark:border-slate-800 rounded-lg font-mono text-sm text-slate-500 dark:text-slate-400 select-none">
                        <span className="text-slate-700 dark:text-slate-300">
                          cerb_
                        </span>
                        <span className="tracking-widest">
                          ••••••••••••••••••••••••••••
                        </span>
                      </div>
                      <p className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                        <Info className="w-3.5 h-3.5 shrink-0 text-blue-400" />
                        The plaintext API key is only shown{' '}
                        <strong>once</strong> upon creation or rotation and
                        cannot be retrieved again. Rotate the key if you've lost
                        access to it.
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* JWT Public Key Card */}
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle>JWT Public Key (RSA)</CardTitle>
                      <CardDescription>
                        Use this on your backend to verify the signature of JWTs
                        issued to your end-users.
                      </CardDescription>
                    </div>
                    <Button
                      onClick={() => setIsRotateJwtModalOpen(true)}
                      variant="outline"
                      size="sm"
                      className="h-7 px-3 text-xs font-medium bg-amber-500/10 text-amber-700 dark:text-amber-500 hover:bg-amber-500/20 border-amber-500/20 transition-colors"
                    >
                      Rotate Key Pair
                    </Button>
                  </CardHeader>
                  <CardContent>
                    {secrets ? (
                      <div className="space-y-3">
                        <div className="flex gap-2 items-start relative">
                          <ScrollArea className="w-full h-35 bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-slate-800 rounded-lg">
                            <pre className="p-4 text-slate-700 dark:text-slate-300 font-mono text-xs whitespace-pre">
                              {showJwt
                                ? secrets.public_key
                                : '-----BEGIN PUBLIC KEY-----\n••••••••••••••••••••••••••••••••••••••••••••••••••••••••••\n••••••••••••••••••••••••••••••••••••••••••••••••••••••••••\n••••••••••••••••••••••••••••••••••••••••••••••••••••••••••\n••••••••••••••••••••••••••••••••••••••••••••••••••••••••••\n-----END PUBLIC KEY-----'}
                            </pre>
                            <ScrollBar orientation="horizontal" />
                          </ScrollArea>
                          <div className="absolute top-2 right-2 flex flex-col gap-2">
                            <Button
                              onClick={() => setShowJwt(!showJwt)}
                              variant="outline"
                              size="icon"
                              className="h-8 w-8 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white bg-slate-100 dark:bg-slate-800 transition-colors"
                            >
                              {showJwt ? (
                                <EyeOff className="w-4 h-4" />
                              ) : (
                                <Eye className="w-4 h-4" />
                              )}
                            </Button>
                            <CopyButton text={secrets.public_key} />
                          </div>
                        </div>
                        <p className="text-xs text-slate-500">
                          Unlike the API key, the public key is safe to retrieve
                          at any time — it is not a secret.
                        </p>
                      </div>
                    ) : (
                      <div className="p-8 flex items-center justify-center">
                        <div className="w-5 h-5 border-2 border-slate-300 dark:border-slate-700 border-t-slate-600 dark:border-t-slate-400 rounded-full animate-spin" />
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </main>
        <AddProviderModal />

        <AlertDialog
          open={isRotateApiModalOpen}
          onOpenChange={setIsRotateApiModalOpen}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Rotate API Key</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure? This will instantly invalidate your current API
                key. Existing apps using the old key will break.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel disabled={rotateApiKey.isPending}>
                Cancel
              </AlertDialogCancel>
              <AlertDialogAction
                onClick={(e) => {
                  e.preventDefault()
                  doRotateApiKey()
                }}
                disabled={rotateApiKey.isPending}
                className="bg-amber-600 text-white hover:bg-amber-700 focus:ring-amber-600"
              >
                {rotateApiKey.isPending ? 'Rotating...' : 'Yes, rotate API Key'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        <AlertDialog
          open={isRotateJwtModalOpen}
          onOpenChange={setIsRotateJwtModalOpen}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Rotate JWT Secret</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure? This generates new RSA keys. All currently issued
                JWTs will fail signature validation on your backend until they
                expire.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel disabled={rotateJwtSecret.isPending}>
                Cancel
              </AlertDialogCancel>
              <AlertDialogAction
                onClick={(e) => {
                  e.preventDefault()
                  doRotateJwtSecret()
                }}
                disabled={rotateJwtSecret.isPending}
                className="bg-amber-600 text-white hover:bg-amber-700 focus:ring-amber-600"
              >
                {rotateJwtSecret.isPending
                  ? 'Rotating...'
                  : 'Yes, rotate JWT keys'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        <AlertDialog
          open={isDeleteModalOpen}
          onOpenChange={(open) => {
            setIsDeleteModalOpen(open)
            if (!open) setDeleteConfirmName('')
          }}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Project</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to permanently delete project{' '}
                <span className="font-bold">{project.name}</span>? All data and
                users will be lost forever.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <div className="py-4">
              <Label className="text-slate-700 dark:text-slate-300">
                Please type <span className="font-bold">{project.name}</span> to
                confirm.
              </Label>
              <Input
                className="mt-2"
                value={deleteConfirmName}
                onChange={(e) => setDeleteConfirmName(e.target.value)}
                placeholder={project.name}
              />
            </div>
            <AlertDialogFooter>
              <AlertDialogCancel disabled={deleteProject.isPending}>
                Cancel
              </AlertDialogCancel>
              <AlertDialogAction
                onClick={(e) => {
                  e.preventDefault()
                  doDeleteProject()
                }}
                disabled={
                  deleteProject.isPending || deleteConfirmName !== project.name
                }
                className="bg-red-600 text-white hover:bg-red-700 focus:ring-red-600"
              >
                {deleteProject.isPending
                  ? 'Deleting...'
                  : 'Yes, delete project'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        <SecretRevealModal
          isOpen={!!revealSecrets}
          onClose={() => setRevealSecrets(null)}
          secrets={revealSecrets}
          mode={revealMode}
        />
      </div>
    </TooltipProvider>
  )
}
