import { createContext, useContext } from 'react'
import type { Project } from '../api/projects'

export interface ProjectContextType {
  project: Project
  publicKey: string
  fetchProject: (showLoader?: boolean) => Promise<void>
}

export const ProjectContext = createContext<ProjectContextType | undefined>(
  undefined,
)

export function useProject() {
  const context = useContext(ProjectContext)
  if (!context) {
    throw new Error('useProject must be used within a Project Layout')
  }
  return context
}
