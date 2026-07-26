import { createFileRoute, useRouter } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  Save,
  Key,
  Shield,
  RefreshCw,
  Trash2,
  Webhook,
  Settings2,
  User,
  Plus,
  AlertTriangle,
  Check,
  Pencil,
  Eye,
  EyeOff,
} from 'lucide-react'
import {
  getProject,
  updateProjectName,
  updateProjectEnvironment,
  updateProjectFrontendUrl,
  updateProjectOrigins,
  updateProjectOAuth,
  rotateApiKey,
  rotateJwtSecret,
  getProjectSecrets,
  updateProjectClaims,
} from '../api/projects'
import type { Project, Environment } from '../api/projects'
import axios from 'axios'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '../components/ui/card'
import { Button, CopyButton, DownloadButton } from '../components/ui/button'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select'
import { toast } from 'sonner'
import { extractErrorMessage, API_URL } from '../lib/api-client'
import { ProjectUsers } from '../components/ProjectUsers'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../components/ui/dialog'
import _Editor from 'react-simple-code-editor'
import Prism from 'prismjs'
import 'prismjs/themes/prism.css'

const Editor = (_Editor as any).default || _Editor

export const Route = createFileRoute(
  '/_protected/projects/$projectId/settings',
)({
  component: ProjectSettingsPage,
})

function ProjectSettingsPage() {
  const { projectId } = Route.useParams()
  const router = useRouter()

  const [project, setProject] = useState<Project | null>(null)
  const [publicKey, setPublicKey] = useState('')
  const [loading, setLoading] = useState(true)
  const [savingGeneral, setSavingGeneral] = useState(false)
  const [generalSaved, setGeneralSaved] = useState(false)
  const [savingAuth, setSavingAuth] = useState(false)
  const [savingOrigins, setSavingOrigins] = useState(false)
  const [savingName, setSavingName] = useState(false)
  const [isEditingName, setIsEditingName] = useState(false)

  // Form states
  const [name, setName] = useState('')
  const [environment, setEnvironment] = useState<Environment>('development')
  const [frontendUrl, setFrontendUrl] = useState('')
  const [allowedOrigins, setAllowedOrigins] = useState<string[]>([])
  const [newOrigin, setNewOrigin] = useState('')
  const [githubClientId, setGithubClientId] = useState('')
  const [githubClientSecret, setGithubClientSecret] = useState('')
  const [googleClientId, setGoogleClientId] = useState('')
  const [googleClientSecret, setGoogleClientSecret] = useState('')
  const [allowedProviders, setAllowedProviders] = useState<string[]>([])
  const [claimsJson, setClaimsJson] = useState('{}')
  const [savingClaims, setSavingClaims] = useState(false)
  const [claimsSaved, setClaimsSaved] = useState(false)
  const [claimsError, setClaimsError] = useState<string>('')
  const [authErrors, setAuthErrors] = useState<Record<string, string>>({})
  const [generalErrors, setGeneralErrors] = useState<Record<string, string>>({})
  const [originError, setOriginError] = useState<string>('')
  const [rsaRotated, setRsaRotated] = useState(false)

  // Auth Modal States
  const [isProviderModalOpen, setIsProviderModalOpen] = useState(false)
  const [editingProvider, setEditingProvider] = useState<string | null>(null)
  const [modalProvider, setModalProvider] = useState<string>('')
  const [modalClientId, setModalClientId] = useState('')
  const [modalClientSecret, setModalClientSecret] = useState('')
  const [providerToDelete, setProviderToDelete] = useState<string | null>(null)

  // Security / Origin Modals
  const [originToDelete, setOriginToDelete] = useState<string | null>(null)

  // Danger Zone Modal
  const [isDeleteProjectModalOpen, setIsDeleteProjectModalOpen] =
    useState(false)

  const [showEnvConfirm, setShowEnvConfirm] = useState(false)
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.location.hash.replace('#', '') || 'general'
    }
    return 'general'
  })

  const [rotatedApiKey, setRotatedApiKey] = useState('')
  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false)
  const [isRotateApiConfirmOpen, setIsRotateApiConfirmOpen] = useState(false)
  const [isRotateRsaConfirmOpen, setIsRotateRsaConfirmOpen] = useState(false)
  const [isPublicKeyVisible, setIsPublicKeyVisible] = useState(false)

  const handleDownloadJson = (data: any, filename: string) => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(JSON.stringify(data, null, 2))
    const downloadAnchorNode = document.createElement('a')
    downloadAnchorNode.setAttribute('href', dataStr)
    downloadAnchorNode.setAttribute('download', filename)
    document.body.appendChild(downloadAnchorNode)
    downloadAnchorNode.click()
    downloadAnchorNode.remove()
  }

  const handleDownloadPem = (text: string, filename: string) => {
    const dataStr =
      'data:application/x-pem-file;charset=utf-8,' + encodeURIComponent(text)
    const downloadAnchorNode = document.createElement('a')
    downloadAnchorNode.setAttribute('href', dataStr)
    downloadAnchorNode.setAttribute('download', filename)
    document.body.appendChild(downloadAnchorNode)
    downloadAnchorNode.click()
    downloadAnchorNode.remove()
  }

  const handleTabChange = (val: string) => {
    setActiveTab(val)
    if (typeof window !== 'undefined') {
      window.location.hash = val
    }
  }

  const fetchProject = async (showLoader = false) => {
    try {
      if (showLoader) setLoading(true)
      const data = await getProject(projectId)
      const secrets = await getProjectSecrets(projectId)
      setProject(data)
      setPublicKey(secrets.public_key)

      // Initialize form states
      setName(data.name)
      setEnvironment(data.environment)
      setFrontendUrl(data.frontend_url || '')
      setAllowedOrigins(data.allowed_origins || [])

      const config = data.oauth_config || {}
      setAllowedProviders(Object.keys(config).filter((k) => config[k]?.enabled))
      setGithubClientId(config.github?.client_id || '')
      setGoogleClientId(config.google?.client_id || '')

      setClaimsJson(JSON.stringify(data.default_claims || {}, null, 2))
      // Note: Secrets are not returned by the API typically
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to fetch project details'))
      router.navigate({ to: '/projects' })
    } finally {
      if (showLoader) setLoading(false)
    }
  }

  useEffect(() => {
    fetchProject(true)
  }, [projectId])

  const handleSaveGeneral = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingGeneral(true)
    setGeneralErrors({})

    if (frontendUrl) {
      const urlSchema = z
        .string()
        .url('Must be a valid URL')
        .refine(
          (val) =>
            val.startsWith('https://') || val.startsWith('http://localhost'),
          { message: 'URL must be HTTPS or http://localhost' },
        )
      const result = urlSchema.safeParse(frontendUrl)
      if (!result.success) {
        setGeneralErrors({ frontendUrl: result.error.issues[0].message })
        setSavingGeneral(false)
        return
      }
    }

    try {
      await updateProjectEnvironment(projectId, environment)
      if (frontendUrl) await updateProjectFrontendUrl(projectId, frontendUrl)
      setGeneralSaved(true)
      setTimeout(() => setGeneralSaved(false), 2000)
      fetchProject(false)
    } catch (error: unknown) {
      if (
        axios.isAxiosError(error) &&
        error.response?.status === 422 &&
        Array.isArray(error.response?.data?.detail)
      ) {
        const errors: Record<string, string> = {}
        error.response.data.detail.forEach((d: any) => {
          const field = d.loc[d.loc.length - 1]
          if (field === 'frontend_url') {
            errors.frontendUrl = d.msg
          } else {
            errors[field] = d.msg
          }
        })
        setGeneralErrors(errors)
      } else {
        toast.error(
          extractErrorMessage(error, 'Failed to update general settings'),
        )
      }
    } finally {
      setSavingGeneral(false)
    }
  }

  const handleUpdateName = async () => {
    if (!name.trim() || name === project?.name) {
      setIsEditingName(false)
      setName(project?.name || '')
      return
    }

    setSavingName(true)
    try {
      await updateProjectName(projectId, name)
      setIsEditingName(false)
      fetchProject(false)
    } catch (error: unknown) {
      if (
        axios.isAxiosError(error) &&
        error.response?.status === 422 &&
        error.response?.data?.detail?.[0]?.msg
      ) {
        toast.error(error.response.data.detail[0].msg)
      } else {
        toast.error(extractErrorMessage(error, 'Failed to update name'))
      }
    } finally {
      setSavingName(false)
    }
  }

  // handleSaveAuth removed because we now save immediately when adding/editing/removing a provider

  const handleAddOrigin = async () => {
    if (!newOrigin.trim()) return
    if (allowedOrigins.length >= 5) {
      toast.error('Maximum of 5 origins allowed.')
      return
    }
    setOriginError('')
    const updatedOrigins = [...allowedOrigins, newOrigin.trim()]
    setSavingOrigins(true)
    try {
      await updateProjectOrigins(projectId, updatedOrigins)
      setAllowedOrigins(updatedOrigins)
      setNewOrigin('')
    } catch (error: unknown) {
      if (
        axios.isAxiosError(error) &&
        error.response?.status === 422 &&
        error.response?.data?.detail?.[0]?.msg
      ) {
        setOriginError(error.response.data.detail[0].msg)
      } else {
        toast.error(extractErrorMessage(error, 'Failed to add origin'))
      }
    } finally {
      setSavingOrigins(false)
    }
  }

  const handleRemoveOrigin = async () => {
    if (!originToDelete) return
    const updatedOrigins = allowedOrigins.filter((o) => o !== originToDelete)
    setSavingOrigins(true)
    try {
      await updateProjectOrigins(projectId, updatedOrigins)
      setAllowedOrigins(updatedOrigins)
      setOriginToDelete(null)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to remove origin'))
    } finally {
      setSavingOrigins(false)
    }
  }

  const handleFormatJson = () => {
    try {
      if (!claimsJson.trim()) return
      const parsed = JSON.parse(claimsJson)
      setClaimsJson(JSON.stringify(parsed, null, 2))
    } catch (e) {
      toast.error('Invalid JSON: Cannot format')
    }
  }

  const handleEditorKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const target = e.target as HTMLTextAreaElement
    const { selectionStart, selectionEnd, value } = target

    const pairs: Record<string, string> = {
      '"': '"',
      "'": "'",
      '{': '}',
      '[': ']',
      '(': ')',
    }

    if (pairs[e.key]) {
      e.preventDefault()
      const closing = pairs[e.key]
      const newValue =
        value.substring(0, selectionStart) +
        e.key +
        closing +
        value.substring(selectionEnd)

      setClaimsJson(newValue)

      // Use requestAnimationFrame or setTimeout to run after React renders the new value
      requestAnimationFrame(() => {
        target.selectionStart = target.selectionEnd = selectionStart + 1
      })
    } else if (
      e.key === 'Backspace' &&
      selectionStart === selectionEnd &&
      selectionStart > 0
    ) {
      const prevChar = value[selectionStart - 1]
      const nextChar = value[selectionStart]
      if (pairs[prevChar] === nextChar) {
        e.preventDefault()
        const newValue =
          value.substring(0, selectionStart - 1) +
          value.substring(selectionEnd + 1)
        setClaimsJson(newValue)
        requestAnimationFrame(() => {
          target.selectionStart = target.selectionEnd = selectionStart - 1
        })
      }
    }
  }

  const handleSaveClaims = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingClaims(true)
    setClaimsError('')
    try {
      const claimsObj = JSON.parse(claimsJson)

      if (
        typeof claimsObj !== 'object' ||
        Array.isArray(claimsObj) ||
        claimsObj === null
      ) {
        setClaimsError('Claims must be a JSON object')
        setSavingClaims(false)
        return
      }

      const claimsSchema = z
        .record(z.string(), z.any())
        .refine(
          (obj) => Object.keys(obj).length <= 10,
          'Maximum 10 custom claims allowed.',
        )
        .refine((obj) => {
          const reserved = [
            'sub',
            'email',
            'exp',
            'iat',
            'jti',
            'project_id',
            'is_verified',
            'family_id',
          ]
          return !Object.keys(obj).some((k) => reserved.includes(k))
        }, 'Cannot use reserved claims.')

      const result = claimsSchema.safeParse(claimsObj)
      if (!result.success) {
        setClaimsError(result.error.issues[0].message)
        setSavingClaims(false)
        return
      }

      await updateProjectClaims(projectId, claimsObj)
      setClaimsSaved(true)
      setTimeout(() => setClaimsSaved(false), 2000)
      fetchProject(false)
    } catch (error: unknown) {
      if (error instanceof SyntaxError) {
        setClaimsError('Invalid JSON format')
      } else if (
        axios.isAxiosError(error) &&
        error.response?.status === 422 &&
        error.response?.data?.detail?.[0]?.msg
      ) {
        setClaimsError(error.response.data.detail[0].msg)
      } else {
        toast.error(extractErrorMessage(error, 'Failed to update claims'))
      }
    } finally {
      setSavingClaims(false)
    }
  }

  const handleRotateApiKey = async () => {
    try {
      const data = await rotateApiKey(projectId)
      setRotatedApiKey(data.api_key)
      setIsRotateApiConfirmOpen(false)
      setIsApiKeyModalOpen(true)
      fetchProject(false)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to rotate API Key'))
    }
  }

  const handleRotateJwtSecret = async () => {
    try {
      const data = await rotateJwtSecret(projectId)
      setPublicKey(data.public_key)
      setIsRotateRsaConfirmOpen(false)
      setRsaRotated(true)
      setTimeout(() => setRsaRotated(false), 2000)
      fetchProject(false)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to rotate RSA Keys'))
    }
  }

  if (loading || !project) {
    return (
      <div className="flex flex-col gap-6 max-w-4xl mx-auto w-full animate-pulse">
        <div className="h-10 bg-taupe/20 w-1/3 mb-4 rounded-none"></div>
        <div className="h-100 bg-taupe/20 w-full rounded-none"></div>
      </div>
    )
  }

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
    <div className="flex flex-col max-w-4xl mx-auto w-full relative">
      <Tabs
        value={activeTab}
        onValueChange={handleTabChange}
        className="w-full"
      >
        <div className="pb-4 mb-4">
          <div className="flex items-center gap-4 mb-8">
            <Button
              variant="outline"
              size="icon"
              className="h-10 w-10 shrink-0"
              onClick={() => router.navigate({ to: `/projects/${projectId}` })}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex flex-col flex-1 min-w-0">
              {isEditingName ? (
                <div className="flex items-center gap-2 h-9">
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="text-3xl font-display font-black tracking-tight text-slate h-full py-0 px-2 -ml-2 bg-taupe/10 border-slate/20 max-w-75"
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleUpdateName()
                      if (e.key === 'Escape') {
                        setName(project.name)
                        setIsEditingName(false)
                      }
                    }}
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleUpdateName}
                    disabled={savingName}
                    className="h-8 w-8 shrink-0"
                  >
                    {savingName ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Check className="w-5 h-5 text-sage" />
                    )}
                  </Button>
                </div>
              ) : (
                <div className="flex items-center gap-3 group h-9 ">
                  <h1 className="text-3xl font-display font-black tracking-tight text-slate truncate">
                    {project.name}
                  </h1>
                  <button
                    onClick={() => setIsEditingName(true)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-slate/40 hover:text-slate shrink-0"
                  >
                    <Pencil className="w-4 h-4" />
                  </button>
                </div>
              )}
              <p className="text-slate/70 font-semibold mt-1 font-mono text-sm truncate">
                ID: {project.id}
              </p>
            </div>
          </div>

          <TabsList className="w-full flex-wrap">
            <TabsTrigger value="general" className="gap-2">
              <Settings2 className="w-4 h-4" /> General
            </TabsTrigger>
            <TabsTrigger value="auth" className="gap-2">
              <Shield className="w-4 h-4" /> Authentication
            </TabsTrigger>
            <TabsTrigger value="users" className="gap-2">
              <User className="w-4 h-4" /> Users
            </TabsTrigger>
            <TabsTrigger value="security" className="gap-2">
              <Key className="w-4 h-4" /> Security
            </TabsTrigger>
            <TabsTrigger value="claims" className="gap-2">
              <Webhook className="w-4 h-4" /> Custom Default Claims
            </TabsTrigger>
          </TabsList>
        </div>

        {/* GENERAL TAB */}
        <TabsContent value="general">
          <form onSubmit={handleSaveGeneral}>
            <Card>
              <CardHeader>
                <CardTitle>General Information</CardTitle>
                <CardDescription>
                  Update your project's core details.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Environment</Label>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between p-6 border-2 border-slate bg-vanilla rounded-xl transition-colors shadow-[4px_4px_0px_rgba(30,41,59,1)] gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-3 h-3 rounded-full ${environment === 'production' ? 'bg-sage' : 'bg-ochre'}`}
                        />
                        <h4 className="font-bold text-lg capitalize text-slate">
                          {environment}
                        </h4>
                      </div>
                      <p className="text-sm font-semibold text-slate/70 mt-1 max-w-lg">
                        {environment === 'development'
                          ? 'Running in dev mode. Limits and caching are relaxed.'
                          : 'Running in production mode. Strict limits applied.'}
                      </p>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setShowEnvConfirm(true)}
                      className="shrink-0 bg-vanilla"
                    >
                      Switch to{' '}
                      {environment === 'development'
                        ? 'Production'
                        : 'Development'}
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="frontendUrl">Frontend Application URL</Label>
                  <Input
                    id="frontendUrl"
                    value={frontendUrl}
                    onChange={(e) => {
                      setFrontendUrl(e.target.value)
                      setGeneralErrors({ ...generalErrors, frontendUrl: '' })
                    }}
                    placeholder="https://myapp.com"
                    className={
                      generalErrors.frontendUrl
                        ? 'border-terracotta focus-visible:ring-terracotta'
                        : ''
                    }
                  />
                  {generalErrors.frontendUrl && (
                    <p className="text-sm font-bold text-terracotta">
                      {generalErrors.frontendUrl}
                    </p>
                  )}
                  <p className="text-xs text-slate/70 font-semibold">
                    Where users should be redirected after successful
                    authentication flows.
                  </p>
                </div>
              </CardContent>
              <CardFooter className="flex justify-end border-t-2 border-taupe/20 pt-6">
                <Button
                  type="submit"
                  disabled={savingGeneral || generalSaved}
                  className={`relative overflow-hidden w-37.5 transition-all duration-300 ${generalSaved ? 'bg-sage! text-vanilla! border-sage!' : ''}`}
                >
                  <AnimatePresence mode="wait">
                    {savingGeneral ? (
                      <motion.div
                        key="saving"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex items-center justify-center gap-2 absolute inset-0"
                      >
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Saving...
                      </motion.div>
                    ) : generalSaved ? (
                      <motion.div
                        key="saved"
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        className="flex items-center justify-center gap-2 absolute inset-0"
                      >
                        <Check className="w-4 h-4" />
                        Saved!
                      </motion.div>
                    ) : (
                      <motion.div
                        key="default"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex items-center justify-center gap-2 absolute inset-0"
                      >
                        <Save className="w-4 h-4" />
                        Save Changes
                      </motion.div>
                    )}
                  </AnimatePresence>
                  {/* Placeholder to maintain button height since absolute content doesn't affect height */}
                  <div className="invisible flex items-center justify-center gap-2">
                    <Save className="w-4 h-4" />
                    Save Changes
                  </div>
                  {generalSaved && (
                    <motion.div
                      initial={{ scale: 0, opacity: 0.4 }}
                      animate={{ scale: 3, opacity: 0 }}
                      transition={{ duration: 0.6, ease: 'easeOut' }}
                      className="absolute inset-0 bg-vanilla rounded-full origin-center pointer-events-none"
                    />
                  )}
                </Button>
              </CardFooter>
            </Card>
          </form>

          <Card className="mt-8 border-terracotta overflow-hidden relative">
            <CardHeader>
              <CardTitle className="text-terracotta">Danger Zone</CardTitle>
              <CardDescription>
                Deleting this project will permanently remove all associated
                users, sessions, and configurations.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                variant="destructive"
                onClick={() => setIsDeleteProjectModalOpen(true)}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Project
              </Button>
            </CardContent>
          </Card>

          <Dialog open={showEnvConfirm} onOpenChange={setShowEnvConfirm}>
            <DialogContent className="sm:max-w-106.25 border-2 border-slate bg-vanilla p-0 overflow-hidden shadow-[8px_8px_0px_rgba(30,41,59,1)]">
              <DialogHeader className="p-6 bg-sand border-b-2 border-slate">
                <DialogTitle className="text-2xl font-black text-slate">
                  Change Environment
                </DialogTitle>
                <DialogDescription className="font-semibold text-slate/70">
                  Are you sure you want to switch to{' '}
                  {environment === 'development' ? 'Production' : 'Development'}
                  ?
                </DialogDescription>
              </DialogHeader>
              <div className="p-6 text-sm text-slate font-semibold">
                {environment === 'development' ? (
                  <p>
                    Switching to production will enforce strict rate limits and
                    caching.
                  </p>
                ) : (
                  <p>
                    Switching to development will relax security constraints and
                    rate limits.
                  </p>
                )}
                <p className="mt-2 text-terracotta">
                  This change will take effect immediately.
                </p>
              </div>
              <DialogFooter className="p-6 bg-sand border-t-2 border-slate flex justify-end">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowEnvConfirm(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="button"
                  onClick={async () => {
                    const newEnv =
                      environment === 'development'
                        ? 'production'
                        : 'development'
                    try {
                      await updateProjectEnvironment(projectId, newEnv)
                      setEnvironment(newEnv)
                      fetchProject(false)
                    } catch (error: unknown) {
                      toast.error(
                        extractErrorMessage(
                          error,
                          'Failed to update environment',
                        ),
                      )
                    } finally {
                      setShowEnvConfirm(false)
                    }
                  }}
                >
                  Confirm Switch
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </TabsContent>

        {/* AUTHENTICATION TAB */}
        <TabsContent value="auth">
          <div className="flex flex-col gap-8">
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
          </div>
        </TabsContent>

        {/* USERS TAB */}
        <TabsContent value="users">
          <ProjectUsers projectId={projectId} />
        </TabsContent>

        {/* SECURITY TAB */}
        <TabsContent value="security">
          <div className="flex flex-col gap-6">
            <Card>
              <CardHeader>
                <CardTitle>CORS & Origins</CardTitle>
                <CardDescription>
                  Control which domains can make API requests using this
                  project's keys.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2 items-center mb-2">
                  <Input
                    placeholder="https://myapp.com"
                    value={newOrigin}
                    onChange={(e) => {
                      setNewOrigin(e.target.value)
                      setOriginError('')
                    }}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddOrigin()}
                    disabled={allowedOrigins.length >= 5}
                    className={
                      originError
                        ? 'border-terracotta focus-visible:ring-terracotta'
                        : ''
                    }
                  />
                  <Button
                    type="button"
                    variant="primary"
                    onClick={handleAddOrigin}
                    disabled={
                      savingOrigins ||
                      !newOrigin.trim() ||
                      allowedOrigins.length >= 5
                    }
                    className="shrink-0"
                  >
                    {savingOrigins ? (
                      <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                    ) : (
                      <Plus className="w-4 h-4 mr-2" />
                    )}
                    Add Origin
                  </Button>
                </div>
                {originError && (
                  <p className="text-sm font-bold text-terracotta mb-2">
                    {originError}
                  </p>
                )}

                {allowedOrigins.length >= 5 && (
                  <p className="text-sm font-bold text-terracotta mb-6">
                    Maximum of 5 origins allowed.
                  </p>
                )}
                {allowedOrigins.length < 5 && <div className="mb-6" />}

                <div className="space-y-3">
                  {allowedOrigins.map((origin, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between items-center bg-vanilla border-2 border-slate shadow-[2px_2px_0px_rgba(30,41,59,1)] p-3 rounded-xl"
                    >
                      <span className="font-mono text-sm font-bold text-slate px-2">
                        {origin}
                      </span>
                      <Button
                        type="button"
                        variant="destructive"
                        size="icon"
                        className="h-8 w-8 shrink-0"
                        onClick={() => setOriginToDelete(origin)}
                        disabled={savingOrigins}
                      >
                        {savingOrigins && originToDelete === origin ? (
                          <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  ))}
                  {allowedOrigins.length === 0 && (
                    <p className="text-sm font-semibold text-slate/50 p-6 border-2 border-dashed border-slate/30 rounded-xl bg-taupe/5 text-center">
                      No origins allowed yet.
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Key Management</CardTitle>
                <CardDescription>
                  Rotate your API keys and JWT signing secrets.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between p-6 border-2 border-slate bg-vanilla rounded-xl shadow-[4px_4px_0px_rgba(30,41,59,1)] gap-4">
                  <div className="flex-1">
                    <h4 className="font-bold text-slate text-lg">API Key</h4>
                    <p className="text-sm font-semibold text-slate/70 mt-1 max-w-lg">
                      Used for backend API integrations. The plaintext key is
                      only shown once when rotated.
                    </p>
                    {project.api_key_last_rotated && (
                      <p className="text-xs font-semibold text-slate/50 mt-2">
                        Last rotated:{' '}
                        {new Date(
                          project.api_key_last_rotated,
                        ).toLocaleString()}
                      </p>
                    )}
                  </div>
                  <Button
                    variant="destructive"
                    onClick={() => setIsRotateApiConfirmOpen(true)}
                    className="gap-2 shrink-0"
                  >
                    <RefreshCw className="w-4 h-4" /> Rotate Key
                  </Button>
                </div>

                <div className="flex flex-col p-6 border-2 border-slate bg-vanilla rounded-xl shadow-[4px_4px_0px_rgba(30,41,59,1)] gap-4">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div className="flex-1">
                      <h4 className="font-bold text-slate text-lg">
                        JWT Public Key (RSA PEM)
                      </h4>
                      <p className="text-sm font-semibold text-slate/70 mt-1 max-w-lg">
                        Used to verify the signatures of JWTs issued by Cerberus
                        to your users. This is safe to share.
                      </p>
                      {project.jwt_secret_last_rotated && (
                        <p className="text-xs font-semibold text-slate/50 mt-2">
                          Last rotated:{' '}
                          {new Date(
                            project.jwt_secret_last_rotated,
                          ).toLocaleString()}
                        </p>
                      )}
                    </div>
                    <Button
                      variant="destructive"
                      onClick={() => setIsRotateRsaConfirmOpen(true)}
                      disabled={rsaRotated}
                      className={`gap-2 shrink-0 relative overflow-hidden transition-all duration-300 w-35 ${rsaRotated ? 'bg-terracotta! text-vanilla! border-terracotta!' : ''}`}
                    >
                      <AnimatePresence mode="wait">
                        {rsaRotated ? (
                          <motion.div
                            key="rotated"
                            initial={{ opacity: 0, scale: 0.5 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.8 }}
                            className="flex items-center justify-center gap-2 absolute inset-0"
                          >
                            <Check className="w-4 h-4" />
                            Rotated!
                          </motion.div>
                        ) : (
                          <motion.div
                            key="default"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="flex items-center justify-center gap-2 absolute inset-0"
                          >
                            <RefreshCw className="w-4 h-4" /> Rotate Keys
                          </motion.div>
                        )}
                      </AnimatePresence>
                      <div className="invisible flex items-center justify-center gap-2">
                        <RefreshCw className="w-4 h-4" /> Rotate Keys
                      </div>
                      {rsaRotated && (
                        <motion.div
                          initial={{ scale: 0, opacity: 0.4 }}
                          animate={{ scale: 3, opacity: 0 }}
                          transition={{ duration: 0.6, ease: 'easeOut' }}
                          className="absolute inset-0 bg-vanilla rounded-full origin-center pointer-events-none"
                        />
                      )}
                    </Button>
                  </div>

                  <div className="mt-2">
                    <div className="relative">
                      <pre className="w-full min-h-30 border-2 border-slate bg-taupe/10 px-4 py-4 text-xs font-mono rounded-xl overflow-hidden whitespace-pre-wrap break-all leading-relaxed">
                        {isPublicKeyVisible
                          ? publicKey
                          : publicKey.replace(
                              /(?<=-----BEGIN PUBLIC KEY-----\n)[\s\S]*?(?=\n-----END PUBLIC KEY-----)/,
                              '****************************************************************\n****************************************************************\n****************************************************************\n****************************************************************',
                            )}
                      </pre>
                      <div className="absolute top-2 right-2 flex gap-3">
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 bg-vanilla shrink-0"
                          onClick={() =>
                            setIsPublicKeyVisible(!isPublicKeyVisible)
                          }
                          title={isPublicKeyVisible ? 'Hide Key' : 'Show Key'}
                        >
                          {isPublicKeyVisible ? (
                            <EyeOff className="w-4 h-4" />
                          ) : (
                            <Eye className="w-4 h-4" />
                          )}
                        </Button>
                        <CopyButton
                          value={publicKey}
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 bg-vanilla shrink-0"
                          title="Copy Key"
                        />
                        <DownloadButton
                          onDownload={() =>
                            handleDownloadPem(
                              publicKey,
                              `${project.name.replace(/\s+/g, '_').toLowerCase()}_public_key.pem`,
                            )
                          }
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 bg-vanilla shrink-0"
                          title="Download PEM"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* CLAIMS TAB */}
        <TabsContent value="claims">
          <form onSubmit={handleSaveClaims}>
            <Card>
              <CardHeader>
                <CardTitle>Custom Default Claims Mapping</CardTitle>
                <CardDescription>
                  Map custom default user metadata into the JWT payloads issued
                  by Cerberus.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-terracotta/10 border-2 border-terracotta p-4 rounded-xl">
                  <div className="text-sm font-semibold text-terracotta flex items-start gap-2">
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    <div>
                      <strong>Reserved Claims:</strong> You cannot map the
                      following reserved claims:
                      <br />
                      <div className="flex flex-wrap gap-1 mt-2">
                        {[
                          'sub',
                          'email',
                          'exp',
                          'iat',
                          'jti',
                          'project_id',
                          'is_verified',
                          'family_id',
                        ].map((claim) => (
                          <code
                            key={claim}
                            className="bg-terracotta/20 px-1.5 py-0.5 rounded text-xs font-mono"
                          >
                            {claim}
                          </code>
                        ))}
                      </div>
                      <span className="text-xs mt-3 block font-bold">
                        Maximum 10 custom claims allowed.
                      </span>
                    </div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="claimsJson">Claims (JSON)</Label>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleFormatJson}
                      className="h-8 text-xs"
                    >
                      Format JSON
                    </Button>
                  </div>
                  <div
                    className={`w-full font-mono text-sm border-2 rounded-xl bg-vanilla focus-within:ring-2 overflow-hidden transition-colors ${claimsError ? 'border-terracotta focus-within:ring-terracotta' : 'border-taupe focus-within:ring-slate'}`}
                  >
                    <Editor
                      value={claimsJson}
                      onValueChange={(val: string) => {
                        setClaimsJson(val)
                        setClaimsError('')
                      }}
                      onKeyDown={handleEditorKeyDown}
                      highlight={(code: string) =>
                        Prism.highlight(
                          code,
                          Prism.languages.javascript || Prism.languages.js,
                          'javascript',
                        )
                      }
                      padding={16}
                      style={{
                        fontFamily:
                          'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                        fontSize: 14,
                        minHeight: '200px',
                      }}
                      textareaId="claimsJson"
                      className="w-full focus-visible:outline-none"
                    />
                  </div>
                  {claimsError && (
                    <p className="text-sm font-bold text-terracotta">
                      {claimsError}
                    </p>
                  )}
                </div>
              </CardContent>
              <CardFooter className="flex justify-end border-t-2 border-taupe/20 pt-6">
                <Button
                  type="submit"
                  disabled={savingClaims || claimsSaved}
                  className={`relative overflow-hidden w-35 transition-all duration-300 ${claimsSaved ? 'bg-sage! text-vanilla! border-sage!' : ''}`}
                >
                  <AnimatePresence mode="wait">
                    {savingClaims ? (
                      <motion.div
                        key="saving"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex items-center justify-center gap-2 absolute inset-0"
                      >
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Saving...
                      </motion.div>
                    ) : claimsSaved ? (
                      <motion.div
                        key="saved"
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        className="flex items-center justify-center gap-2 absolute inset-0"
                      >
                        <Check className="w-4 h-4" />
                        Saved!
                      </motion.div>
                    ) : (
                      <motion.div
                        key="default"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex items-center justify-center gap-2 absolute inset-0"
                      >
                        <Save className="w-4 h-4" />
                        Save Claims
                      </motion.div>
                    )}
                  </AnimatePresence>
                  {/* Placeholder to maintain button height since absolute content doesn't affect height */}
                  <div className="invisible flex items-center gap-2">
                    <Save className="w-4 h-4" />
                    Save Claims
                  </div>
                  {claimsSaved && (
                    <motion.div
                      initial={{ scale: 0, opacity: 0.4 }}
                      animate={{ scale: 3, opacity: 0 }}
                      transition={{ duration: 0.6, ease: 'easeOut' }}
                      className="absolute inset-0 bg-vanilla rounded-full origin-center pointer-events-none"
                    />
                  )}
                </Button>
              </CardFooter>
            </Card>
          </form>
        </TabsContent>
      </Tabs>

      <Dialog open={isApiKeyModalOpen} onOpenChange={setIsApiKeyModalOpen}>
        <DialogContent className="sm:max-w-xl">
          <div className="space-y-6">
            <DialogHeader>
              <DialogTitle className="text-2xl font-black text-slate flex items-center gap-2">
                API Key Rotated!
              </DialogTitle>
              <DialogDescription className="text-terracotta font-bold flex items-start gap-2 mt-2 bg-terracotta/10 p-3 border-2 border-terracotta rounded-xl">
                <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                Warning: This is the ONLY time you will see this new API Key.
                Please copy it or download the JSON file now.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-slate font-bold">
                  New API Key (Keep Secret)
                </Label>
                <div className="flex gap-2">
                  <Input
                    value={rotatedApiKey}
                    readOnly
                    className="font-mono bg-taupe/10"
                  />
                  <CopyButton value={rotatedApiKey} />
                </div>
              </div>
            </div>

            <DialogFooter className="flex gap-2 sm:justify-between border-t-2 border-taupe/20 pt-4 mt-6">
              <DownloadButton
                variant="outline"
                size="default"
                onDownload={() =>
                  handleDownloadJson(
                    { api_key: rotatedApiKey },
                    `${project.name.replace(/\s+/g, '_').toLowerCase()}_api_key.json`,
                  )
                }
                className="gap-2"
              >
                Download JSON
              </DownloadButton>
              <Button
                onClick={() => {
                  setIsApiKeyModalOpen(false)
                  setRotatedApiKey('')
                }}
              >
                I've Saved It
              </Button>
            </DialogFooter>
          </div>
        </DialogContent>
      </Dialog>
      <Dialog
        open={isRotateApiConfirmOpen}
        onOpenChange={setIsRotateApiConfirmOpen}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl font-black text-terracotta flex items-center gap-2">
              <AlertTriangle className="w-6 h-6" /> Rotate API Key?
            </DialogTitle>
            <DialogDescription className="text-slate/80 font-semibold pt-4">
              Are you sure you want to rotate the API Key? This action will{' '}
              <strong className="text-terracotta">instantly break</strong> any
              existing backend integrations using the old key.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-6 flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setIsRotateApiConfirmOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleRotateApiKey}>
              Yes, Rotate Key
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={isRotateRsaConfirmOpen}
        onOpenChange={setIsRotateRsaConfirmOpen}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl font-black text-terracotta flex items-center gap-2">
              <AlertTriangle className="w-6 h-6" /> Rotate RSA Keys?
            </DialogTitle>
            <DialogDescription className="text-slate/80 font-semibold pt-4">
              Are you sure you want to rotate the RSA Keys? This will{' '}
              <strong className="text-terracotta">instantly invalidate</strong>{' '}
              all active user sessions for this project.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-6 flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setIsRotateRsaConfirmOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleRotateJwtSecret}>
              Yes, Rotate Keys
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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

      <Dialog
        open={!!originToDelete}
        onOpenChange={(open) => !open && setOriginToDelete(null)}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl font-black text-terracotta flex items-center gap-2">
              <AlertTriangle className="w-6 h-6" /> Remove Origin?
            </DialogTitle>
            <DialogDescription className="text-slate/80 font-semibold pt-4">
              Are you sure you want to remove{' '}
              <strong className="break-all">{originToDelete}</strong> from your
              allowed origins? This domain will immediately lose access to the
              API.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-6 flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOriginToDelete(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleRemoveOrigin}
              disabled={savingOrigins}
            >
              {savingOrigins ? (
                <RefreshCw className="w-4 h-4 animate-spin mr-2" />
              ) : null}
              Remove
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={isDeleteProjectModalOpen}
        onOpenChange={setIsDeleteProjectModalOpen}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl font-black text-terracotta flex items-center gap-2">
              <AlertTriangle className="w-6 h-6" /> Delete Project?
            </DialogTitle>
            <DialogDescription className="text-slate/80 font-semibold pt-4">
              Are you absolutely sure you want to delete this project? This
              action is{' '}
              <strong className="text-terracotta">
                permanent and cannot be undone
              </strong>
              . All users, settings, and keys will be destroyed.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-6 flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setIsDeleteProjectModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                toast.error(
                  'Project deletion is not fully implemented in this demo.',
                )
                setIsDeleteProjectModalOpen(false)
              }}
            >
              Yes, Delete Project
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
