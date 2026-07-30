import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { RefreshCw, Plus, Trash2, AlertTriangle, Eye, EyeOff, Check } from 'lucide-react'
import { toast } from 'sonner'
import { extractErrorMessage } from '../lib/api-client'
import { useProject } from '../contexts/ProjectContext'
import { updateProjectOrigins, rotateApiKey, rotateJwtSecret } from '../api/projects'
import { CopyButton, DownloadButton } from '../components/ui/button'
import { handleDownloadPem } from '../lib/utils'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../components/ui/dialog'
import { Label } from '../components/ui/label'

export const Route = createFileRoute(
  '/_protected/projects/$projectId/security',
)({
  component: SecurityTab,
})

function SecurityTab() {
  const { projectId } = Route.useParams()
  const { project, publicKey, fetchProject } = useProject()

  const [allowedOrigins, setAllowedOrigins] = useState<string[]>([])
  const [newOrigin, setNewOrigin] = useState('')
  const [originError, setOriginError] = useState('')
  const [savingOrigins, setSavingOrigins] = useState(false)
  const [originToDelete, setOriginToDelete] = useState<string | null>(null)

  const [isRotateApiConfirmOpen, setIsRotateApiConfirmOpen] = useState(false)
  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false)
  const [rotatedApiKey, setRotatedApiKey] = useState('')

  const [isRotateRsaConfirmOpen, setIsRotateRsaConfirmOpen] = useState(false)
  const [rsaRotated, setRsaRotated] = useState(false)
  const [isPublicKeyVisible, setIsPublicKeyVisible] = useState(false)

  // Sync with layout state
  useEffect(() => {
    if (project) {
      setAllowedOrigins(project.allowed_origins || [])
    }
  }, [project])

  const handleAddOrigin = async () => {
    if (!newOrigin.trim()) return

    try {
      new URL(newOrigin) // Basic valid URL test
    } catch {
      setOriginError('Must be a valid URL (e.g., https://example.com)')
      return
    }

    if (allowedOrigins.length >= 5) {
      setOriginError('Maximum of 5 origins allowed.')
      return
    }

    setSavingOrigins(true)
    setOriginError('')

    const originWithoutPath = new URL(newOrigin).origin
    const updatedOrigins = [...allowedOrigins, originWithoutPath]

    try {
      await updateProjectOrigins(projectId, updatedOrigins)
      setAllowedOrigins(updatedOrigins)
      setNewOrigin('')
      fetchProject(false)
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
      fetchProject(false)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to remove origin'))
    } finally {
      setSavingOrigins(false)
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
      await rotateJwtSecret(projectId)
      setIsRotateRsaConfirmOpen(false)
      setRsaRotated(true)
      setTimeout(() => setRsaRotated(false), 2000)
      fetchProject(false)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to rotate RSA Keys'))
    }
  }

  return (
    <div className="flex flex-col gap-6 w-full animate-in fade-in slide-in-from-bottom-2 duration-300">
      <Card>
        <CardHeader>
          <CardTitle>CORS & Origins</CardTitle>
          <CardDescription>
            Control which domains can make API requests using this project's
            keys.
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
                savingOrigins || !newOrigin.trim() || allowedOrigins.length >= 5
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
                Used for backend API integrations. The plaintext key is only
                shown once when rotated.
              </p>
              {project?.api_key_last_rotated && (
                <p className="text-xs font-semibold text-slate/50 mt-2">
                  Last rotated:{' '}
                  {new Date(project.api_key_last_rotated).toLocaleString()}
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
                  Used to verify the signatures of JWTs issued by Cerberus to
                  your users. This is safe to share.
                </p>
                {project?.jwt_secret_last_rotated && (
                  <p className="text-xs font-semibold text-slate/50 mt-2">
                    Last rotated:{' '}
                    {new Date(project.jwt_secret_last_rotated).toLocaleString()}
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
                    onClick={() => setIsPublicKeyVisible(!isPublicKeyVisible)}
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
                        `${project?.name.replace(/\s+/g, '_').toLowerCase()}_public_key.pem`,
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
                    className="font-mono bg-taupe/10 border-2 border-slate/20 text-slate"
                  />
                  <CopyButton value={rotatedApiKey} className="h-10 w-10" />
                </div>
              </div>

            </div>

            <DialogFooter className="sm:justify-between flex-row items-center">
              <DownloadButton
                size="default"
                variant="outline"
                onDownload={() => {
                  const blob = new Blob(
                    [
                      JSON.stringify(
                        {
                          project_id: project?.id,
                          project_name: project?.name,
                          api_key: rotatedApiKey,
                          rotated_at: new Date().toISOString(),
                        },
                        null,
                        2,
                      ),
                    ],
                    { type: 'application/json' },
                  )
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `cerberus_${project?.name.replace(/\s+/g, '_').toLowerCase()}_api_key.json`
                  document.body.appendChild(a)
                  a.click()
                  document.body.removeChild(a)
                  URL.revokeObjectURL(url)
                }}
                className="gap-2"
                title="Download JSON"
              >
                Download JSON
              </DownloadButton>
              <Button onClick={() => setIsApiKeyModalOpen(false)}>
                I've stored it safely
              </Button>
            </DialogFooter>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
