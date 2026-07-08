import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '#/lib/api'

export interface ProviderConfig {
  enabled: boolean
  client_id?: string | null
  client_secret?: string | null
  client_secret_configured?: boolean
}

export interface OAuthConfig {
  [provider: string]: ProviderConfig
  local: ProviderConfig
}

export interface OAuthProvider {
  key: string
  display_name: string
  scopes: string[]
  required_fields: string[]
}

export interface Project {
  id: string
  name: string
  created_at: string
  tenant_id?: string
  oauth_config?: OAuthConfig
  allowed_origins?: string[]
  environment: 'development' | 'production'
  frontend_url?: string | null
}

export interface ProjectCreateRes extends Project {
  api_key: string
  public_key: string
}

export interface ProjectSecretsRes {
  api_key_hash: string
  public_key: string
}

export interface ProjectRotateKeysRes {
  api_key: string
  public_key: string
}

export function useProjects() {
  const queryClient = useQueryClient()

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const res = await api.get<Project[]>('/projects/')
      return res.data
    },
  })

  const createProject = useMutation({
    mutationFn: async (data: { name: string }) => {
      const res = await api.post<ProjectCreateRes>('/projects/', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })

  const deleteProject = useMutation({
    mutationFn: async (projectId: string) => {
      await api.delete(`/projects/${projectId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })

  const updateProjectOauth = useMutation({
    mutationFn: async ({
      projectId,
      oauth_config,
    }: {
      projectId: string
      oauth_config: Record<string, any>
    }) => {
      const res = await api.put<Project>(`/projects/${projectId}/oauth`, {
        oauth_config,
      })
      return res.data
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const updateProjectOrigins = useMutation({
    mutationFn: async ({
      projectId,
      allowed_origins,
    }: {
      projectId: string
      allowed_origins: string[]
    }) => {
      const res = await api.put<Project>(`/projects/${projectId}/origins`, {
        allowed_origins,
      })
      return res.data
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const updateProjectEnvironment = useMutation({
    mutationFn: async ({
      projectId,
      environment,
    }: {
      projectId: string
      environment: 'development' | 'production'
    }) => {
      const res = await api.put<Project>(`/projects/${projectId}/environment`, {
        environment,
      })
      return res.data
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const updateProjectName = useMutation({
    mutationFn: async ({
      projectId,
      name,
    }: {
      projectId: string
      name: string
    }) => {
      const res = await api.put<Project>(`/projects/${projectId}/name`, {
        name,
      })
      return res.data
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const updateProjectFrontendUrl = useMutation({
    mutationFn: async ({
      projectId,
      frontend_url,
    }: {
      projectId: string
      frontend_url: string
    }) => {
      const res = await api.put<Project>(
        `/projects/${projectId}/frontend-url`,
        { frontend_url },
      )
      return res.data
    },
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const rotateApiKey = useMutation({
    mutationFn: async (projectId: string) => {
      const res = await api.post<{ api_key: string }>(
        `/projects/${projectId}/keys/rotate-api-key`,
      )
      return res.data
    },
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const rotateJwtSecret = useMutation({
    mutationFn: async (projectId: string) => {
      const res = await api.post<{ public_key: string }>(
        `/projects/${projectId}/keys/rotate-jwt-secret`,
      )
      return res.data
    },
    onSuccess: (data, projectId) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      queryClient.setQueryData(
        ['project', projectId, 'secrets'],
        (old: any) => {
          if (!old) return old
          return { ...old, public_key: data.public_key }
        },
      )
    },
  })

  return {
    projects: projects || [],
    isLoading,
    createProject,
    deleteProject,
    updateProjectOauth,
    updateProjectOrigins,
    updateProjectEnvironment,
    updateProjectName,
    updateProjectFrontendUrl,
    rotateApiKey,
    rotateJwtSecret,
  }
}

export function useOAuthProviders() {
  return useQuery({
    queryKey: ['oauth-providers'],
    queryFn: async () => {
      const res = await api.get<OAuthProvider[]>('/projects/oauth-providers')
      return res.data
    },
  })
}

export function useProjectSecrets(projectId: string) {
  return useQuery({
    queryKey: ['project', projectId, 'secrets'],
    queryFn: async () => {
      const res = await api.get<ProjectSecretsRes>(
        `/projects/${projectId}/secrets`,
      )
      return res.data
    },
    enabled: !!projectId,
  })
}
