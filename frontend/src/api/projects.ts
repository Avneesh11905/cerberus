import { apiClient } from '../lib/api-client'

export type Environment = 'development' | 'production'

export interface Project {
  id: string
  name: string
  environment: Environment
  frontend_url?: string
  allowed_origins: string[]
  oauth_config: Record<
    string,
    {
      enabled: boolean
      client_id?: string
      client_secret_configured?: boolean
    }
  >
  default_claims: Record<string, string>
  created_at: string
  updated_at: string
  api_key_preview?: string
  api_key_last_rotated?: string
  jwt_secret_last_rotated?: string
}

export interface PaginatedProjectsRes {
  items: Project[]
  total: number
  page: number
  size: number
}

export const getProjects = async (params?: {
  page: number
  size: number
}): Promise<PaginatedProjectsRes> => {
  const { data } = await apiClient.get<PaginatedProjectsRes>('/projects/', {
    params,
  })
  return data
}

export const getProject = async (projectId: string): Promise<Project> => {
  const { data } = await apiClient.get<Project>(`/projects/${projectId}`)
  return data
}

export interface ProjectCreateRes {
  id: string
  name: string
  api_key: string
  public_key: string
  created_at: string
}

export const createProject = async (payload: {
  name: string
  environment: Environment
}): Promise<ProjectCreateRes> => {
  const { data } = await apiClient.post<ProjectCreateRes>('/projects/', payload)
  return data
}

export const updateProjectName = async (
  projectId: string,
  name: string,
): Promise<Project> => {
  const { data } = await apiClient.put<Project>(`/projects/${projectId}/name`, {
    name,
  })
  return data
}

export const updateProjectEnvironment = async (
  projectId: string,
  environment: Environment,
): Promise<Project> => {
  const { data } = await apiClient.put<Project>(
    `/projects/${projectId}/environment`,
    { environment },
  )
  return data
}

export const updateProjectFrontendUrl = async (
  projectId: string,
  frontendUrl: string,
): Promise<Project> => {
  const { data } = await apiClient.put<Project>(
    `/projects/${projectId}/frontend-url`,
    { frontend_url: frontendUrl },
  )
  return data
}

export const updateProjectOrigins = async (
  projectId: string,
  allowedOrigins: string[],
): Promise<Project> => {
  const { data } = await apiClient.put<Project>(
    `/projects/${projectId}/origins`,
    { allowed_origins: allowedOrigins },
  )
  return data
}

export const updateProjectOAuth = async (
  projectId: string,
  payload: {
    oauth_config: Record<
      string,
      {
        enabled: boolean
        client_id?: string | null
        client_secret?: string | null
      }
    >
  },
): Promise<Project> => {
  const { data } = await apiClient.put<Project>(
    `/projects/${projectId}/oauth`,
    payload,
  )
  return data
}

export const updateProjectClaims = async (
  projectId: string,
  claims: Record<string, unknown>,
): Promise<Project> => {
  const { data } = await apiClient.put<Project>(
    `/projects/${projectId}/claims`,
    { claims },
  )
  return data
}

export const deleteProject = async (projectId: string): Promise<void> => {
  await apiClient.delete(`/projects/${projectId}`)
}

export const rotateApiKey = async (
  projectId: string,
): Promise<{ api_key: string }> => {
  const { data } = await apiClient.post<{ api_key: string }>(
    `/projects/${projectId}/keys/rotate-api-key`,
  )
  return data
}

export const rotateJwtSecret = async (
  projectId: string,
): Promise<{ public_key: string }> => {
  const { data } = await apiClient.post<{ public_key: string }>(
    `/projects/${projectId}/keys/rotate-jwt-secret`,
  )
  return data
}

export const getProjectSecrets = async (
  projectId: string,
): Promise<{ public_key: string }> => {
  const { data } = await apiClient.get<{ public_key: string }>(
    `/projects/${projectId}/secrets`,
  )
  return data
}

export interface ProjectUser {
  id: string
  email: string
  name?: string
  is_active: boolean
  created_at: string
  updated_at: string
  last_login?: string
}

export interface PaginatedProjectUsersRes {
  items: ProjectUser[]
  total: number
  page: number
  size: number
}

export const getProjectUsers = async (
  projectId: string,
  page: number = 1,
  size: number = 50,
  search: string = '',
): Promise<PaginatedProjectUsersRes> => {
  const params = new URLSearchParams()
  params.append('page', page.toString())
  params.append('size', size.toString())
  if (search) params.append('search', search)
  const { data } = await apiClient.get<PaginatedProjectUsersRes>(
    `/projects/${projectId}/users?${params.toString()}`,
  )
  return data
}

export interface ProjectUserStatusUpdateRes {
  message: string
  user_id: string
  is_active: boolean
}

export const getTenantUsers = async (
  page: number = 1,
  size: number = 50,
  search: string = '',
): Promise<PaginatedProjectUsersRes> => {
  const params = new URLSearchParams()
  params.append('page', page.toString())
  params.append('size', size.toString())
  if (search) params.append('search', search)
  const { data } = await apiClient.get<PaginatedProjectUsersRes>(
    `/projects/users?${params.toString()}`,
  )
  return data
}

export const updateProjectUserStatus = async (
  projectId: string,
  userId: string,
  isActive: boolean,
): Promise<ProjectUserStatusUpdateRes> => {
  const { data } = await apiClient.put<ProjectUserStatusUpdateRes>(
    `/projects/${projectId}/users/${userId}/status`,
    { is_active: isActive },
  )
  return data
}

export interface UserClaimsRes {
  user_id: string
  default_claims: Record<string, unknown>
  user_overrides: Record<string, unknown>
  effective_claims: Record<string, unknown>
}

export const getProjectUserClaims = async (
  projectId: string,
  userId: string,
): Promise<UserClaimsRes> => {
  const { data } = await apiClient.get<UserClaimsRes>(
    `/projects/${projectId}/users/${userId}/claims`,
  )
  return data
}

export const updateProjectUserClaims = async (
  projectId: string,
  userId: string,
  overrides: Record<string, unknown>,
): Promise<UserClaimsRes> => {
  const { data } = await apiClient.patch<UserClaimsRes>(
    `/projects/${projectId}/users/${userId}/claims`,
    { overrides },
  )
  return data
}

export const updateTenantUserStatus = async (
  email: string,
  isActive: boolean,
): Promise<{ message: string; updated_projects: string[] }> => {
  const { data } = await apiClient.post<{
    message: string
    updated_projects: string[]
  }>(`/projects/users/${email}/status`, { is_active: isActive })
  return data
}
