import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// Safe storage for SSR environments (TanStack Start)
const safeStorage = {
  getItem: (name: string) => {
    if (typeof window === 'undefined') return null;
    return window.localStorage.getItem(name);
  },
  setItem: (name: string, value: string) => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(name, value);
  },
  removeItem: (name: string) => {
    if (typeof window === 'undefined') return;
    window.localStorage.removeItem(name);
  },
};

export interface User {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
}

interface AuthState {
  accessToken: string | null;
  user: User | null;
  setAuth: (accessToken: string, user: User) => void;
  setAccessToken: (accessToken: string | null) => void;
  setUser: (user: User) => void;
  unverifiedEmail: string | null;
  setUnverifiedEmail: (email: string | null) => void;
  verifiedEmail: string | null;
  setVerifiedEmail: (email: string | null) => void;
  otpExpiresAt: number | null;
  setOtpExpiresAt: (timestamp: number | null) => void;
  resendAvailableAt: number | null;
  setResendAvailableAt: (timestamp: number | null) => void;
  logout: () => void;
  isCheckingSession: boolean;
  setIsCheckingSession: (val: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      unverifiedEmail: null,
      verifiedEmail: null,
      otpExpiresAt: null,
      resendAvailableAt: null,
      isCheckingSession: true,
      setIsCheckingSession: (isCheckingSession) => set({ isCheckingSession }),
      setAuth: (accessToken, user) => set({ accessToken, user }),
      setAccessToken: (accessToken) => set({ accessToken }),
      setUser: (user) => set({ user }),
      setUnverifiedEmail: (unverifiedEmail) => set({ unverifiedEmail }),
      setVerifiedEmail: (verifiedEmail) => set({ verifiedEmail }),
      setOtpExpiresAt: (otpExpiresAt) => set({ otpExpiresAt }),
      setResendAvailableAt: (resendAvailableAt) => set({ resendAvailableAt }),
      logout: () => set({ accessToken: null, user: null, unverifiedEmail: null, verifiedEmail: null, otpExpiresAt: null, resendAvailableAt: null }),
    }),
    {
      name: 'cerberus-auth',
      storage: createJSONStorage(() => safeStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
        unverifiedEmail: state.unverifiedEmail,
        verifiedEmail: state.verifiedEmail,
        otpExpiresAt: state.otpExpiresAt,
        resendAvailableAt: state.resendAvailableAt,
      }),
      // We only want to persist the user data (for quick UI render before validating),
      // or we can persist both. The access token is usually short-lived.
      // We will persist both for now, but rely on the API client's 401 interceptor
      // to refresh it if it's expired.
    }
  )
);
