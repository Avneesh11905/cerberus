import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '#/lib/api'
import type { User } from '#/lib/auth'

export interface SystemLogRes {
  id: string
  created_at: string
  level: string
  event_type: string
  message: string
  details?: Record<string, any>
  tenant_id?: string
  user_id?: string
}

export function useAdmin() {
  const queryClient = useQueryClient()

  const { data: tenants, isLoading: isLoadingTenants } = useQuery({
    queryKey: ['admin', 'tenants'],
    queryFn: async () => {
      const res = await api.get<User[]>('/admin/tenants')
      return res.data
    },
  })

  const updateTenantStatus = useMutation({
    mutationFn: async ({
      tenantId,
      is_active,
    }: {
      tenantId: string
      is_active: boolean
    }) => {
      const res = await api.patch<User>(`/admin/tenants/${tenantId}/status`, {
        is_active,
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'tenants'] })
    },
  })

  return {
    tenants: tenants || [],
    isLoadingTenants,
    updateTenantStatus,
  }
}

export function useAdminLogs(
  page: number = 1,
  limit: number = 50,
  level?: string,
  source?: string,
) {
  return useQuery({
    queryKey: ['admin', 'logs', page, limit, level, source],
    queryFn: async () => {
      const offset = (page - 1) * limit
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      })
      if (level) params.append('level', level)
      if (source) params.append('source', source)

      const res = await api.get<SystemLogRes[]>(
        `/admin/logs?${params.toString()}`,
      )
      return res.data
    },
    //  Keep previous page data visible while fetching next page (no flash)
    placeholderData: (prev) => prev,
  })
}
