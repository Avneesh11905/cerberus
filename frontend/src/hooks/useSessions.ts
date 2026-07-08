import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, setAccessToken, setCsrfToken } from '#/lib/api'

export interface Session {
  family_id: string
  ip_address: string | null
  user_agent: string | null
  created_at: string
  last_active: string
  is_current: boolean
  auth_provider: string
}

export function useSessions() {
  const queryClient = useQueryClient()

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: async () => {
      const res = await api.get<Session[]>('/auth/sessions')
      return res.data
    },
  })

  const revokeSession = useMutation({
    mutationFn: async (familyId: string) => {
      await api.delete(`/auth/sessions/${familyId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
  })

  const revokeAllSessions = useMutation({
    mutationFn: async () => {
      await api.post('/auth/logout/all')
    },
    onSuccess: () => {
      //  Clear in-memory tokens before navigating. Without this, the SPA-level
      // accessToken survives the redirect and can be used for ~15 min after logout.
      setAccessToken(null)
      setCsrfToken(null)
      queryClient.setQueryData(['me'], null)
      queryClient.clear()
      window.location.href = '/'
    },
  })

  return {
    sessions: sessions || [],
    isLoading,
    revokeSession,
    revokeAllSessions,
  }
}
