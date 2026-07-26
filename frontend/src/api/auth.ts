import { apiClient } from '../lib/api-client'

export interface ChangePasswordReq {
  current_password?: string
  new_password: string
}

export const updatePassword = async (data: ChangePasswordReq) => {
  const response = await apiClient.patch('/auth/password/', data)
  return response.data
}

export const getSessions = async () => {
  const response = await apiClient.get('/auth/sessions')
  return response.data
}

export const revokeSession = async (familyId: string) => {
  const response = await apiClient.delete(`/auth/sessions/${familyId}`)
  return response.data
}

export const revokeAllSessions = async () => {
  const response = await apiClient.post('/auth/logout/all')
  return response.data
}
