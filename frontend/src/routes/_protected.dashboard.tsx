import { createFileRoute, Link } from '@tanstack/react-router'
import { useState } from 'react'
import { Skeleton } from '#/components/ui/skeleton'
import { Label } from '#/components/ui/label'
import { Plus, FolderOpen, Trash2, Github, Code2 } from 'lucide-react'
import { useProjects } from '#/hooks/useProjects'
import { SecretRevealModal } from '#/components/SecretRevealModal'
import { ScrollArea } from '#/components/ui/scroll-area'
import { SidebarTrigger } from '#/components/ui/sidebar'
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from '#/components/ui/context-menu'
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '#/components/ui/dialog'
import { Button } from '#/components/ui/button'
import { Input } from '#/components/ui/input'

export const Route = createFileRoute('/_protected/dashboard')({
  beforeLoad: () => {
    // Admins and tenants can access this page
  },
  component: DashboardOverview,
})

function DashboardOverview() {
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')
  const [revealSecrets, setRevealSecrets] = useState<any>(null)
  const [projectToDelete, setProjectToDelete] = useState<{
    id: string
    name: string
  } | null>(null)

  const { projects, isLoading, createProject, deleteProject } = useProjects()

  const handleDeleteProject = async () => {
    if (projectToDelete) {
      await deleteProject.mutateAsync(projectToDelete.id)
      setProjectToDelete(null)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const result = await createProject.mutateAsync({ name: newProjectName })
      setRevealSecrets({
        api_key: result.api_key,
        public_key: result.public_key,
      })
      setIsCreateOpen(false)
      setNewProjectName('')
    } catch (err) {
      console.error('Failed to create project', err)
    }
  }

  return (
    <div className="flex flex-col h-full bg-transparent">
      <header className="flex h-14 items-center gap-4 border-b border-slate-200/50 dark:border-slate-800/50 backdrop-blur-md bg-white/70 dark:bg-[#0a0a0a]/70 px-4 shrink-0 sticky top-0 z-50">
        <SidebarTrigger />
        <h1 className="font-semibold text-lg">Dashboard</h1>
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

      <ScrollArea className="flex-1 w-full">
        <div className="max-w-6xl w-full mx-auto p-8">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                  Projects
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Manage your Cerberus Identity projects.
                </p>
              </div>
              <Button onClick={() => setIsCreateOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Project
              </Button>
            </div>

            {isLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <Skeleton className="h-40 rounded-2xl" />
                <Skeleton className="h-40 rounded-2xl" />
                <Skeleton className="h-40 rounded-2xl" />
              </div>
            ) : projects.length === 0 ? (
              <div className="flex flex-col items-center justify-center p-12 border border-slate-200 dark:border-slate-800 border-dashed rounded-2xl bg-slate-50 dark:bg-[#0a0a0a] text-center">
                <div className="w-12 h-12 bg-blue-50 dark:bg-blue-500/10 rounded-xl flex items-center justify-center mb-4">
                  <FolderOpen className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                  No projects found
                </h3>
                <p className="text-slate-500 dark:text-slate-400 mt-2 max-w-sm mb-6">
                  Get started by creating your first project to manage
                  authentications, API keys, and settings.
                </p>
                <Button onClick={() => setIsCreateOpen(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create your first Project
                </Button>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {projects.map((project) => (
                  <ContextMenu key={project.id}>
                    <ContextMenuTrigger asChild>
                      <Link
                        to="/projects/$projectId"
                        params={{ projectId: project.id }}
                        className="p-6 border border-border rounded-2xl bg-card text-card-foreground hover:shadow-md transition-all group block relative overflow-hidden"
                      >
                        <div className="absolute inset-0 bg-linear-to-br from-transparent via-transparent to-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                        <div className="relative z-10">
                          <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
                            {project.name}
                          </h3>
                          <div className="mt-6 flex items-center justify-between text-xs font-medium">
                            <span className="text-muted-foreground">
                              Created{' '}
                              {new Date(
                                project.created_at,
                              ).toLocaleDateString()}
                            </span>
                            {project.environment === 'development' ? (
                              <span className="bg-amber-500/10 text-amber-500 px-2.5 py-1 rounded-md border border-amber-500/20">
                                Dev
                              </span>
                            ) : (
                              <span className="bg-emerald-500/10 text-emerald-500 px-2.5 py-1 rounded-md border border-emerald-500/20">
                                Prod
                              </span>
                            )}
                          </div>
                        </div>
                      </Link>
                    </ContextMenuTrigger>
                    <ContextMenuContent>
                      <ContextMenuItem
                        className="text-destructive focus:text-destructive focus:bg-destructive/10"
                        onClick={() =>
                          setProjectToDelete({
                            id: project.id,
                            name: project.name,
                          })
                        }
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete Project
                      </ContextMenuItem>
                    </ContextMenuContent>
                  </ContextMenu>
                ))}
              </div>
            )}

            <SecretRevealModal
              isOpen={revealSecrets !== null}
              onClose={() => setRevealSecrets(null)}
              secrets={revealSecrets}
              mode="project_created"
            />

            <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Create Project</DialogTitle>
                  <DialogDescription>
                    Create a new project to start managing authentication.
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleCreate} className="space-y-6 pt-2">
                  <div className="space-y-2">
                    <Label>Project Name</Label>
                    <Input
                      type="text"
                      value={newProjectName}
                      onChange={(e) => setNewProjectName(e.target.value)}
                      placeholder="e.g. My Next.js App"
                      autoFocus
                      required
                    />
                  </div>
                  <div className="flex justify-end gap-3 pt-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setIsCreateOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button type="submit" disabled={createProject.isPending}>
                      {createProject.isPending
                        ? 'Creating...'
                        : 'Create Project'}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>

            <AlertDialog
              open={!!projectToDelete}
              onOpenChange={(open) => !open && setProjectToDelete(null)}
            >
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete Project</AlertDialogTitle>
                  <AlertDialogDescription>
                    Are you sure you want to permanently delete project{' '}
                    <span className="font-bold">{projectToDelete?.name}</span>?
                    All data and users will be lost forever.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel disabled={deleteProject.isPending}>
                    Cancel
                  </AlertDialogCancel>
                  <AlertDialogAction
                    onClick={(e) => {
                      e.preventDefault()
                      handleDeleteProject()
                    }}
                    disabled={deleteProject.isPending}
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  >
                    {deleteProject.isPending
                      ? 'Deleting...'
                      : 'Yes, delete project'}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
