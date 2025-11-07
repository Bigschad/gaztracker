import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginRequest } from '../types';
import { authService } from '../services/api';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  clearError: () => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.login(credentials);

          // Store tokens
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);

          set({
            user: response.user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail || 'Login failed. Please try again.';
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authService.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Clear everything regardless of API call success
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            error: null,
          });
        }
      },

      refreshUser: async () => {
        try {
          const user = await authService.getCurrentUser();
          set({ user });
        } catch (error) {
          console.error('Failed to refresh user:', error);
          get().logout();
        }
      },

      setUser: (user: User | null) => {
        set({ user, isAuthenticated: user !== null });
      },

      setTokens: (accessToken: string, refreshToken: string) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        set({ accessToken, refreshToken, isAuthenticated: true });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
