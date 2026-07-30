import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { RefreshCw, Check, Save, Trash2, AlertTriangle } from 'lucide-react'
import { toast } from 'sonner'
import { extractErrorMessage } from '../lib/api-client'
import { useProject } from '../contexts/ProjectContext'
import { updateProjectEnvironment, updateProjectFrontendUrl } from '../api/projects'
import type { Environment } from '../api/projects'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../components/ui/dialog'

export const Route = createFileRoute(
  '/_protected/projects/$projectId/general',
)({
  component: GeneralTab,
})

function GeneralTab() {
  const { projectId } = Route.useParams()
  const { project, fetchProject } = useProject()

  const [environment, setEnvironment] = useState<Environment>('development')
  const [frontendUrl, setFrontendUrl] = useState('')
  const [savingGeneral, setSavingGeneral] = useState(false)
  const [generalSaved, setGeneralSaved] = useState(false)
  const [generalErrors, setGeneralErrors] = useState<Record<string, string>>({})
  const [showEnvConfirm, setShowEnvConfirm] = useState(false)
  const [isDeleteProjectModalOpen, setIsDeleteProjectModalOpen] = useState(false)

  useEffect(() => {
    if (project) {
      setEnvironment(project.environment)
      setFrontendUrl(project.frontend_url || '')
    }
  }, [project])

  const handleSaveGeneral = async (e: React.FormEvent) => {
    e.preventDefault()
    setGeneralErrors({})

    let hasErrors = false
    const errors: Record<string, string> = {}

    if (frontendUrl && !frontendUrl.match(/^https?:\/\/.+/)) {
      errors.frontendUrl = 'Must be a valid URL starting with http:// or https://'
      hasErrors = true
    }

    if (hasErrors) {
      setGeneralErrors(errors)
      return
    }

    setSavingGeneral(true)
    try {
      if (frontendUrl !== project?.frontend_url) {
        await updateProjectFrontendUrl(projectId, frontendUrl)
      }
      setGeneralSaved(true)
      await fetchProject(false)
      setTimeout(() => setGeneralSaved(false), 2000)
    } catch (error: unknown) {
      toast.error(extractErrorMessage(error, 'Failed to save general settings'))
    } finally {
      setSavingGeneral(false)
    }
  }

  return (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
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
              {environment === 'development' ? 'Production' : 'Development'}?
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
                    extractErrorMessage(error, 'Failed to update environment'),
                  )
                } finally {
                  setShowEnvConfirm(false)
                }
              }}
            >
              Confirm Change
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
