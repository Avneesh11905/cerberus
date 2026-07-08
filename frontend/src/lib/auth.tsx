import type React from 'react';
import { createContext, useContext } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api, setAccessToken, setCsrfToken } from './api';

export interface User {
  id: string;
  email: string;
  role: 'user' | 'tenant' | 'admin';
  project_id: string | null;
  name?: string;
  picture?: string;
  receive_updates?: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  logout: () => Promise<void>;
  login: (data: { email: string; password: string }) => Promise<void>;
  verifyEmail: (data: { email: string; otp: string }) => Promise<void>;
  updateProfile: (data: { name?: string; picture?: string; receive_updates?: boolean }) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      try {
        // Silently refresh token on initial load before trying to get user
        const refreshResponse = await api.post('/auth/refresh');
        if (refreshResponse.status === 204 || !refreshResponse.data?.access_token) {
          return null;
        }
        setAccessToken(refreshResponse.data.access_token);
        if (refreshResponse.data.csrf_token) {
          setCsrfToken(refreshResponse.data.csrf_token);
        }
      } catch (e) {
        // No valid refresh token cookie exists, so they are cleanly logged out
        return null;
      }

      const response = await api.get<User>('/users/me');
      return response.data;
    },
    retry: false, // Don't retry on 401s
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout API failed:', error);
    } finally {
      setAccessToken(null);
      setCsrfToken(null);
      queryClient.setQueryData(['me'], null);
      queryClient.clear();
    }
  };

  const login = async (data: { email: string; password: string }) => {
    const res = await api.post('/auth/login/local', data);
    if (res.data?.csrf_token) {
      setCsrfToken(res.data.csrf_token);
    }
    if (res.data?.access_token) {
      setAccessToken(res.data.access_token);
    }
    if (res.data?.user) {
      queryClient.setQueryData(['me'], res.data.user);
    }
  };

  const verifyEmail = async (data: { email: string; otp: string }) => {
    await api.post('/auth/verify-email', data);
    await queryClient.refetchQueries({ queryKey: ['me'] });
  };

  const updateProfile = async (data: { name?: string; picture?: string; receive_updates?: boolean }) => {
    await api.patch('/users/me', data);
    await queryClient.refetchQueries({ queryKey: ['me'] });
  };

  //  Use only isLoading (first fetch) not isFetching (includes background refetches)
  // to prevent a flash of the loading screen on window focus or query invalidation.
  const isAuthLoading = isLoading;

  return (
    <AuthContext.Provider value={{ user: user || null, isLoading: isAuthLoading, logout, login, verifyEmail, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
