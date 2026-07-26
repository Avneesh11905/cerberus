import { apiClient } from '../lib/api-client'

export interface Metric {
  date: string
  api_requests: number
  login_successes: number
  login_failures: number
  registrations: number
  active_users: number
}

export interface QueryAnalyticsResponse {
  metrics: Metric[]
}

export const getProjectAnalytics = async (
  projectId: string,
  startDate?: string,
  endDate?: string,
): Promise<Metric[]> => {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)

  const query = params.toString() ? `?${params.toString()}` : ''
  const { data } = await apiClient.get<QueryAnalyticsResponse>(
    `/analytics/projects/${projectId}${query}`,
  )
  return data.metrics
}

export const getTenantAnalytics = async (
  tenantId: string,
  startDate?: string,
  endDate?: string,
): Promise<Metric[]> => {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)

  const query = params.toString() ? `?${params.toString()}` : ''
  const { data } = await apiClient.get<QueryAnalyticsResponse>(
    `/analytics/tenants/${tenantId}${query}`,
  )

  return data.metrics
}
