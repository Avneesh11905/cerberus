import { apiClient } from '../lib/api-client';
import type { User } from '../store/auth';

export interface PaginatedTenantRes {
  items: User[];
  total: number;
  page: number;
  size: number;
}

export interface SystemLog {
  id: string;
  created_at: string;
  level: string;
  source: string;
  message: string;
  file?: string;
  line?: number;
}

export interface PaginatedSystemLogRes {
  items: SystemLog[];
  total: number;
  page: number;
  size: number;
}

export interface SystemAnalytics {
  total_tenants: number;
  active_tenants: number;
  total_projects: number;
  active_projects: number;
  total_users: number;
  active_users: number;
  last_updated: string;
}

export const getTenants = async (page: number = 1, size: number = 50, search?: string) => {
  const params: Record<string, unknown> = { page, size };
  if (search) params.search = search;
  const { data } = await apiClient.get<PaginatedTenantRes>('/superadmin/tenants', { params });
  return data;
};

export const updateTenantStatus = async (tenantId: string, isActive: boolean) => {
  const { data } = await apiClient.patch<User>(`/superadmin/tenants/${tenantId}/status`, { is_active: isActive });
  return data;
};

export const updateTenantRole = async (tenantId: string, role: string) => {
  const { data } = await apiClient.patch<User>(`/superadmin/tenants/${tenantId}/role`, { role });
  return data;
};

export const getSystemLogs = async (page: number = 1, limit: number = 100, level?: string) => {
  const params: Record<string, unknown> = { page, limit };
  if (level) params.level = level;
  const { data } = await apiClient.get<PaginatedSystemLogRes>('/superadmin/logs', { params });
  return data;
};

export const getSystemAnalytics = async () => {
  const { data } = await apiClient.get<SystemAnalytics>('/superadmin/analytics');
  return data;
};
