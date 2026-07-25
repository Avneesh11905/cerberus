import { apiClient } from '../lib/api-client';
import type { User } from '../store/auth';

export interface ProfileUpdateReq {
  name?: string;
  picture?: string;
  receive_updates?: boolean;
}

export const getMe = async (): Promise<User> => {
  const response = await apiClient.get<User>('/users/me');
  return response.data;
};

export const updateProfile = async (data: ProfileUpdateReq): Promise<User> => {
  const response = await apiClient.patch<User>('/users/me', data);
  return response.data;
};

export const deleteMe = async () => {
  const response = await apiClient.delete('/users/me');
  return response.data;
};
