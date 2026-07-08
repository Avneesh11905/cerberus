import axios from 'axios';

// Backend URL is usually mapped via proxy in dev, or direct in prod.
// Since we are running the backend on localhost:8000, we'll use that as default.
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // IMPORTANT: Allows sending/receiving HttpOnly cookies
  xsrfCookieName: 'csrf_token', // Required for CSRF protection
  xsrfHeaderName: 'X-CSRF', // Required for CSRF protection
  headers: {
    'Content-Type': 'application/json',
  },
});

let accessToken: string | null = null;
let csrfToken: string | null = null;
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

export const setAccessToken = (token: string | null) => {
  accessToken = token;
};

/**
 * Store the CSRF token in memory after a successful /auth/exchange call.
 * Needed because the csrf_token cookie is host-only on cerberus-api.aymahajan.in
 * and cannot be read via document.cookie on the dashboard origin (cerberus.aymahajan.in).
 */
export const setCsrfToken = (token: string | null) => {
  csrfToken = token;
};

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  // Attach CSRF token for state-mutating requests.
  // Prefer the in-memory value set by setCsrfToken() after an OAuth exchange
  // (needed because the csrf_token cookie is host-only on cerberus-api and
  // cannot be read via document.cookie on the dashboard origin).
  // Fall back to reading document.cookie for any edge cases.
  if (csrfToken) {
    config.headers['X-CSRF'] = csrfToken;
  } else if (typeof document !== 'undefined') {
    const match = document.cookie.match(/(?:^|; )csrf_token=([^;]*)/);
    if (match) {
      config.headers['X-CSRF'] = decodeURIComponent(match[1]);
    }
  }
  
  return config;
});

// Interceptor to unwrap API errors cleanly and handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Token refresh logic for 401 Unauthorized
    const requestUrl = typeof originalRequest.url === 'string'
      ? new URL(originalRequest.url, API_URL).pathname
      : ''
    const skipRefreshEndpoints = new Set([
      '/auth/refresh',
      '/auth/exchange',
      '/auth/login/local',
      '/auth/register',
      '/auth/register/tenant',
      '/auth/verify-email',
      '/auth/verify-email/resend',
      '/auth/password/forgot',
      '/auth/password/reset',
    ])

    if (error.response?.status === 401 && !originalRequest._retry && !skipRefreshEndpoints.has(requestUrl)) {
      if (isRefreshing) {
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = 'Bearer ' + token;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await api.post('/auth/refresh');
        const token = response.data?.access_token;
        if (!token) {
           throw new Error("No valid refresh token returned");
        }
        if (response.data?.csrf_token) {
          setCsrfToken(response.data.csrf_token);
        }
        setAccessToken(token);
        processQueue(null, token);
        originalRequest.headers.Authorization = 'Bearer ' + token;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        setAccessToken(null);
        // We do not reject here so the app can gracefully degrade to unauthenticated state
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    if (error.response?.data?.detail) {
      const detail = error.response.data.detail;
      // Handle simple string details
      if (typeof detail === 'string') {
        error.message = detail;
      }
      // Handle validation array details (FastAPI Pydantic errors)
      else if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) {
        error.message = detail[0].msg;
      }
    }
    return Promise.reject(error);
  }
);

