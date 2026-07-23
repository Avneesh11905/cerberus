import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../store/auth';

export function extractErrorMessage(error: any, fallback = 'An error occurred'): string {
  if (!error) return fallback;
  
  const detail = error.response?.data?.detail;
  const data = error.response?.data;

  if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) return String(detail[0].msg);
  if (typeof detail === 'string') return detail;
  if (typeof detail === 'object' && detail !== null && detail.msg) return String(detail.msg);

  if (Array.isArray(data) && data.length > 0 && data[0].msg) return String(data[0].msg);
  if (typeof data === 'object' && data !== null && data.msg) return String(data.msg);

  if (typeof error === 'string') return error;
  if (error.message) return String(error.message);

  return fallback;
}

export const API_URL = 'http://localhost:8000/v1' ;

export const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Crucial for sending the HTTP-only refresh cookie
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().accessToken;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const isAuthRoute = originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/verify-email') || originalRequest.url?.includes('/auth/refresh') || originalRequest.url?.includes('/auth/password');

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isAuthRoute) {
      // If we are already trying to refresh, queue the request
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = 'Bearer ' + token;
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // The backend expects a POST to /auth/refresh with the refresh_token cookie automatically attached
        const { data } = await axios.post<{ access_token: string }>(
          `${API_URL}/auth/refresh`,
          {},
          { withCredentials: true }
        );

        const newAccessToken = data.access_token;
        useAuthStore.getState().setAccessToken(newAccessToken);
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        processQueue(null, newAccessToken);
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as Error, null);
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
