import { createFileRoute, Link } from '@tanstack/react-router'
import React, { useState, useEffect } from 'react'
import { Plus, ShieldCheck, Activity, CalendarDays, AlertTriangle, Eye, EyeOff, Edit2, Trash2 } from 'lucide-react'
import { getProjects, createProject, updateProjectName, deleteProject, type Project } from '../api/projects'
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "../components/ui/context-menu"
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'
import { Button, CopyButton, DownloadButton } from '../components/ui/button'
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from '../components/ui/dialog'
import { Label } from '../components/ui/label'
import { Input } from '../components/ui/input'
import { Skeleton } from '../components/ui/skeleton'
import { toast } from 'sonner'
import { extractErrorMessage } from '../lib/api-client'

export const Route = createFileRoute('/_protected/projects/')({
  component: ProjectsIndexPage,
})

function ProjectsIndexPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')
  const [creating, setCreating] = useState(false)
  const [createdCredentials, setCreatedCredentials] = useState<{api_key: string, public_key: string, name: string} | null>(null)
  const [showApiKey, setShowApiKey] = useState(false)
  const [showPublicKey, setShowPublicKey] = useState(false)
  
  const [projectToRename, setProjectToRename] = useState<Project | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const [isRenaming, setIsRenaming] = useState(false)
  
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)



  const handleDownloadApiKey = () => {
    if (!createdCredentials) return
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ api_key: createdCredentials.api_key }, null, 2))
    const downloadAnchorNode = document.createElement('a')
    downloadAnchorNode.setAttribute("href", dataStr)
    downloadAnchorNode.setAttribute("download", `${createdCredentials.name.replace(/\s+/g, '_').toLowerCase()}_api_key.json`)
    document.body.appendChild(downloadAnchorNode)
    downloadAnchorNode.click()
    downloadAnchorNode.remove()
  }

  const handleDownloadPublicKey = () => {
    if (!createdCredentials) return
    const dataStr = "data:application/x-pem-file;charset=utf-8," + encodeURIComponent(createdCredentials.public_key)
    const downloadAnchorNode = document.createElement('a')
    downloadAnchorNode.setAttribute("href", dataStr)
    downloadAnchorNode.setAttribute("download", `${createdCredentials.name.replace(/\s+/g, '_').toLowerCase()}_public_key.pem`)
    document.body.appendChild(downloadAnchorNode)
    downloadAnchorNode.click()
    downloadAnchorNode.remove()
  }

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const data = await getProjects()
      setProjects(data)
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to fetch projects'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newProjectName.trim()) return

    setCreating(true)
    try {
      const res = await createProject({ name: newProjectName, environment: 'development' })
      setCreatedCredentials({ api_key: res.api_key, public_key: res.public_key, name: res.name })
      setShowApiKey(false)
      setShowPublicKey(false)
      setNewProjectName('')
      fetchProjects()
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to create project'))
    } finally {
      setCreating(false)
    }
  }

  const handleRenameProject = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!projectToRename || !renameValue.trim()) return
    setIsRenaming(true)
    try {
      await updateProjectName(projectToRename.id, renameValue.trim())
      setProjectToRename(null)
      fetchProjects()
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to rename project'))
    } finally {
      setIsRenaming(false)
    }
  }

  const handleDeleteProject = async () => {
    if (!projectToDelete) return
    setIsDeleting(true)
    try {
      await deleteProject(projectToDelete.id)
      setProjectToDelete(null)
      fetchProjects()
    } catch (err) {
      toast.error(extractErrorMessage(err, 'Failed to delete project'))
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div className="flex flex-col gap-8 max-w-6xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-display font-black tracking-tight text-slate">Projects</h1>
          <p className="text-slate/70 font-semibold mt-1">Manage your applications and environments.</p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="primary" className="gap-2" onClick={() => setCreatedCredentials(null)}>
              <Plus className="w-4 h-4" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-xl">
            {createdCredentials ? (
              <div className="space-y-6">
                <DialogHeader>
                  <DialogTitle className="text-2xl font-black text-slate flex items-center gap-2">
                    Project Created: <span className="text-sage">{createdCredentials.name}</span>
                  </DialogTitle>
                  <DialogDescription className="text-terracotta font-bold flex items-start gap-2 mt-2 bg-terracotta/10 p-3 border-2 border-terracotta rounded-xl">
                    <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                    Warning: This is the ONLY time you will see this API Key. Please copy it or download the JSON file now. If you lose it, you will need to rotate the key.
                  </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-slate font-bold">API Key (Keep Secret)</Label>
                    <div className="flex gap-2">
                      <Input 
                        type={showApiKey ? "text" : "password"}
                        value={createdCredentials.api_key} 
                        readOnly 
                        className="font-mono bg-taupe/10 rounded-xl" 
                      />
                      <Button variant="outline" type="button" className="rounded-xl px-3" onClick={() => setShowApiKey(!showApiKey)}>
                        {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </Button>
                      <CopyButton value={createdCredentials.api_key} />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-slate font-bold">JWT Public Key (RSA PEM)</Label>
                    <div className="relative">
                      <pre className="w-full min-h-30 border-2 border-slate bg-taupe/10 px-4 py-4 text-xs font-mono rounded-xl overflow-hidden whitespace-pre-wrap break-all leading-relaxed">
                        {showPublicKey ? createdCredentials.public_key : createdCredentials.public_key.replace(/(?<=-----BEGIN PUBLIC KEY-----\n)[\s\S]*?(?=\n-----END PUBLIC KEY-----)/, '****************************************************************\n****************************************************************\n****************************************************************\n****************************************************************')}
                      </pre>
                      <div className="absolute top-2 right-2 flex gap-3">
                        <Button type="button" variant="outline" size="icon" className="h-8 w-8 bg-vanilla shrink-0" onClick={() => setShowPublicKey(!showPublicKey)} title={showPublicKey ? "Hide Key" : "Show Key"}>
                          {showPublicKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </Button>
                        <CopyButton value={createdCredentials.public_key} variant="outline" size="icon" className="h-8 w-8 bg-vanilla shrink-0" title="Copy Key" />
                      </div>
                    </div>
                  </div>
                </div>

                <DialogFooter className="flex flex-col sm:flex-row gap-4 sm:gap-2 sm:justify-between border-t-2 border-taupe/20 pt-4 mt-6">
                  <div className="flex gap-2">
                    <DownloadButton variant="outline" size="default" onDownload={handleDownloadApiKey} className="gap-2">
                      API Key (JSON)
                    </DownloadButton>
                    <DownloadButton variant="outline" size="default" onDownload={handleDownloadPublicKey} className="gap-2">
                      Public Key (PEM)
                    </DownloadButton>
                  </div>
                  <Button onClick={() => { setIsDialogOpen(false); setCreatedCredentials(null) }}>
                    I've Saved Them
                  </Button>
                </DialogFooter>
              </div>
            ) : (
              <form onSubmit={handleCreateProject}>
                <DialogHeader>
                  <DialogTitle>Create New Project</DialogTitle>
                  <DialogDescription>
                    Enter a name for your new Cerberus integration project.
                  </DialogDescription>
                </DialogHeader>
                
                <div className="py-6 space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Project Name</Label>
                    <Input 
                      id="name" 
                      placeholder="e.g. Acme Dashboard" 
                      value={newProjectName}
                      onChange={(e) => setNewProjectName(e.target.value)}
                      autoFocus
                    />
                  </div>
                </div>

                <DialogFooter>
                  <DialogClose asChild>
                    <Button variant="outline" type="button">Cancel</Button>
                  </DialogClose>
                  <Button type="submit" disabled={creating || !newProjectName.trim()}>
                    {creating ? 'Creating...' : 'Create Project'}
                  </Button>
                </DialogFooter>
              </form>
            )}
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <Card key={i} className="relative overflow-hidden flex flex-col justify-between min-h-[240px] border-taupe/40 shadow-none bg-vanilla">
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start mb-2">
                  <Skeleton className="w-20 h-6 rounded-none" />
                </div>
                <Skeleton className="w-3/4 h-8 mt-2" />
              </CardHeader>
              <CardContent className="flex flex-col gap-4 py-4">
                <div className="flex items-center gap-3">
                  <Skeleton className="w-4 h-4 shrink-0" />
                  <Skeleton className="w-1/2 h-4" />
                </div>
                <div className="flex items-center gap-3">
                  <Skeleton className="w-4 h-4 shrink-0" />
                  <Skeleton className="w-5/12 h-4" />
                </div>
                <div className="flex items-center gap-3">
                  <Skeleton className="w-4 h-4 shrink-0" />
                  <Skeleton className="w-2/3 h-4" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (!projects || projects.length === 0) ? (
        <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-taupe bg-sand text-center">
          <FolderKanban className="w-12 h-12 text-slate/50 mb-4" />
          <h3 className="text-xl font-bold text-slate mb-2">No Projects Found</h3>
          <p className="text-slate/70 mb-6 font-semibold max-w-sm">Create your first project to start authenticating users and managing environments.</p>
          <Button onClick={() => setIsDialogOpen(true)}>Create Project</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {(projects || []).map(project => (
            <ContextMenu key={project.id}>
              <ContextMenuTrigger asChild>
                <Link
                  to="/projects/$projectId/settings"
                  params={{ projectId: project.id }}
                  className="block group h-full outline-none focus-visible:ring-2 focus-visible:ring-slate"
                >
                  <Card className="relative overflow-hidden flex flex-col justify-between h-full hover:bg-sand/80 transition-all duration-300 ease-out cursor-pointer group-hover:-translate-y-1 group-hover:shadow-[4px_4px_0px_0px_var(--taupe)]">
                    <CardHeader className="pb-4">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-none border-2 border-slate text-xs font-bold uppercase bg-vanilla text-slate">
                          <div className={`w-2 h-2 rounded-full ${project.environment === 'production' ? 'bg-sage' : 'bg-ochre'}`} />
                          {project.environment}
                        </div>
                      </div>
                      <CardTitle className="text-2xl mt-2 line-clamp-1 transition-colors group-hover:text-sage">{project.name}</CardTitle>
                    </CardHeader>

                    <CardContent className="flex flex-col gap-3 py-4">
                       <div className="flex items-center gap-3 text-sm font-semibold text-slate/80">
                          <ShieldCheck className="w-4 h-4 text-taupe" />
                          {Object.values(project.oauth_config || {}).filter(c => c.enabled).length} Auth Providers
                       </div>
                       <div className="flex items-center gap-3 text-sm font-semibold text-slate/80">
                          <Activity className="w-4 h-4 text-taupe" />
                          {project.allowed_origins?.length || 0} Allowed Origins
                       </div>
                       <div className="flex items-center gap-3 text-sm font-semibold text-slate/80">
                          <CalendarDays className="w-4 h-4 text-taupe" />
                          Created {new Date(project.created_at).toLocaleDateString()}
                       </div>
                    </CardContent>
                  </Card>
                </Link>
              </ContextMenuTrigger>
              <ContextMenuContent className="w-48 bg-vanilla border-2 border-slate rounded-xl shadow-[4px_4px_0px_rgba(96,114,116,1)] overflow-hidden p-1 z-60">
                <ContextMenuItem 
                  className="font-bold cursor-pointer rounded-lg px-3 py-2 hover:bg-sand focus:bg-sand"
                  onClick={() => {
                    setProjectToRename(project)
                    setRenameValue(project.name)
                  }}>
                  <Edit2 className="w-4 h-4 mr-2" /> Rename Project
                </ContextMenuItem>
                <ContextMenuItem 
                  className="font-bold cursor-pointer rounded-lg px-3 py-2 text-terracotta hover:bg-terracotta/10 hover:text-terracotta focus:bg-terracotta/10 focus:text-terracotta"
                  onClick={() => setProjectToDelete(project)}>
                  <Trash2 className="w-4 h-4 mr-2" /> Delete Project
                </ContextMenuItem>
              </ContextMenuContent>
            </ContextMenu>
          ))}
        </div>
      )}

      {/* Rename Dialog */}
      <Dialog open={!!projectToRename} onOpenChange={(open) => !open && setProjectToRename(null)}>
        <DialogContent className="sm:max-w-md">
          <form onSubmit={handleRenameProject}>
            <DialogHeader>
              <DialogTitle>Rename Project</DialogTitle>
              <DialogDescription>
                Enter a new name for your project.
              </DialogDescription>
            </DialogHeader>
            <div className="py-6">
              <Label htmlFor="rename">Project Name</Label>
              <Input
                id="rename"
                value={renameValue}
                onChange={(e) => setRenameValue(e.target.value)}
                autoFocus
                className="mt-2"
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setProjectToRename(null)}>Cancel</Button>
              <Button type="submit" disabled={isRenaming || !renameValue.trim() || renameValue.trim() === projectToRename?.name}>
                {isRenaming ? 'Renaming...' : 'Save Changes'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={!!projectToDelete} onOpenChange={(open) => !open && setProjectToDelete(null)}>
        <DialogContent className="sm:max-w-md border-terracotta">
          <DialogHeader>
            <DialogTitle className="text-terracotta flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Delete Project
            </DialogTitle>
            <DialogDescription className="mt-2">
              Are you absolutely sure you want to delete <strong className="text-slate font-bold">{projectToDelete?.name}</strong>? 
              This action cannot be undone and will permanently destroy the project and all its users.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-6 gap-2 sm:justify-between">
            <Button type="button" variant="outline" onClick={() => setProjectToDelete(null)}>Cancel</Button>
            <Button type="button" variant="primary" className="bg-terracotta hover:bg-terracotta/90 text-white" disabled={isDeleting} onClick={handleDeleteProject}>
              {isDeleting ? 'Deleting...' : 'Yes, delete project'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function FolderKanban(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
      <path d="M9 10v4" />
      <path d="M12 10v2" />
      <path d="M15 10v6" />
    </svg>
  )
}
