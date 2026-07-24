import { apiClient } from '../lib/api-client';

export interface ProfileUpdateReq {
  name?: string;
  picture?: string;
  receive_updates?: boolean;
}

export const getMe = async () => {
  const response = await apiClient.get('/users/me');
  return response.data;
};

export const updateProfile = async (data: ProfileUpdateReq) => {
  const response = await apiClient.patch('/users/me', data);
  return response.data;
};

export const deleteMe = async () => {
  const response = await apiClient.delete('/users/me');
  return response.data;
};
