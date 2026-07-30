import { createFileRoute, Outlet, useRouter, useLocation } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { getProject, getProjectSecrets } from '../api/projects'
import type { Project } from '../api/projects'
import { Button } from '../components/ui/button'
import { ArrowLeft, Activity, Settings2, Shield, User, Key, Webhook, Pencil, RefreshCw, Check, Copy, List, RefreshCcw } from 'lucide-react'
import { toast } from 'sonner'
import { extractErrorMessage } from '../lib/api-client'
import { Input } from '../components/ui/input'
import { updateProjectName } from '../api/projects'
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
  ContextMenuSeparator,
} from '../components/ui/context-menu'

import { ProjectContext } from '../contexts/ProjectContext'

export const Route = createFileRoute('/_protected/projects/$projectId')({
  component: ProjectLayout,
})

function ProjectLayout() {
  const { projectId } = Route.useParams()
  const router = useRouter()
  const location = useLocation()

  const [project, setProject] = useState<Project | null>(null)
  const [publicKey, setPublicKey] = useState('')
  const [loading, setLoading] = useState(true)

  const [isEditingName, setIsEditingName] = useState(false)
  const [name, setName] = useState('')
  const [savingName, setSavingName] = useState(false)

  const fetchProjectData = async (showLoader = false) => {
    try {
      if (showLoader) setLoading(true)
      const data = await getProject(projectId)
      const secrets = await getProjectSecrets(projectId)
      setProject(data)
      setPublicKey(secrets.public_key)
      setName(data.name)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to fetch project details'))
      router.navigate({ to: '/projects' })
    } finally {
      if (showLoader) setLoading(false)
    }
  }

  useEffect(() => {
    fetchProjectData(true)
  }, [projectId])

  const handleUpdateName = async () => {
    if (!name.trim() || name === project?.name) {
      setIsEditingName(false)
      setName(project?.name || '')
      return
    }
    setSavingName(true)
    try {
      await updateProjectName(projectId, name)
      toast.success('Project name updated')
      await fetchProjectData()
      setIsEditingName(false)
    } catch (error: unknown) {
      toast.error(extractErrorMessage(error, 'Failed to update project name'))
    } finally {
      setSavingName(false)
    }
  }

  if (loading || !project) {
    return (
      <div className="max-w-7xl mx-auto flex flex-col gap-8 w-full">
        <div className="flex flex-col gap-6 max-w-4xl mx-auto w-full animate-pulse">
          <div className="h-12 w-64 bg-slate/10 rounded-xl"></div>
          <div className="h-96 w-full bg-slate/10 rounded-xl"></div>
        </div>
      </div>
    )
  }

  const currentTab = location.pathname.split('/').pop() || 'analytics'

  const tabs = [
    { id: 'analytics', label: 'Analytics', icon: Activity, to: `/projects/${projectId}/analytics` },
    { id: 'general', label: 'General', icon: Settings2, to: `/projects/${projectId}/general` },
    { id: 'auth', label: 'Authentication', icon: Shield, to: `/projects/${projectId}/auth` },
    { id: 'users', label: 'Users', icon: User, to: `/projects/${projectId}/users` },
    { id: 'security', label: 'Security', icon: Key, to: `/projects/${projectId}/security` },
    { id: 'claims', label: 'Custom Default Claims', icon: Webhook, to: `/projects/${projectId}/claims` },
  ]

  return (
    <ProjectContext.Provider value={{ project, publicKey, fetchProject: fetchProjectData }}>
      <ContextMenu>
        <ContextMenuTrigger asChild>
          <div className="w-full min-h-[calc(100vh-100px)] flex flex-col px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto flex flex-col w-full relative">
            <div className="pb-4 mb-4">
          <div className="w-full flex-wrap flex items-center justify-start rounded-xl bg-slate/5 p-1 text-slate/70 flat-shadow-slate border-2 border-slate mb-8">
            {tabs.map((tab) => {
              const isActive = currentTab === tab.id || (currentTab === projectId && tab.id === 'analytics')
              return (
                <button
                  key={tab.id}
                  onClick={() => router.navigate({ to: tab.to })}
                  className={`inline-flex flex-1 items-center justify-center whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-bold ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 gap-2 ${
                    isActive
                      ? 'bg-vanilla text-slate shadow-sm border-2 border-slate'
                      : 'border-2 border-transparent hover:text-slate hover:bg-slate/5'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </div>

          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="icon"
              className="h-10 w-10 shrink-0"
              onClick={() => router.navigate({ to: `/projects` })}
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
                <div className="flex items-center gap-3 group h-9">
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
        </div>
        
        <div className="mt-2">
          <Outlet />
        </div>
        </div>
        </div>
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] p-1 z-60">
        <ContextMenuItem
          className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
          onClick={() => {
            navigator.clipboard.writeText(project.id)
            toast.success('Project ID copied to clipboard')
          }}
        >
          <Copy className="w-4 h-4 mr-2" /> Copy Project ID
        </ContextMenuItem>
        <ContextMenuItem
          className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
          onClick={() => fetchProjectData()}
        >
          <RefreshCcw className="w-4 h-4 mr-2" /> Refresh Data
        </ContextMenuItem>
        <ContextMenuSeparator className="bg-slate/10 my-1" />
        <ContextMenuItem
          className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
          onClick={() => router.navigate({ to: '/dashboard' })}
        >
          <List className="w-4 h-4 mr-2" /> Back to Projects List
        </ContextMenuItem>
      </ContextMenuContent>
      </ContextMenu>
    </ProjectContext.Provider>
  )
}
