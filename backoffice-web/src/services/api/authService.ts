import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  LoginRequest,
  LoginResponse,
  TokenRefreshRequest,
  TokenRefreshResponse,
  User,
} from '../../types';

export const authService = {
  // Login
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    );
    return response.data;
  },

  // Logout
  logout: async (): Promise<void> => {
    await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
  },

  // Refresh token
  refreshToken: async (data: TokenRefreshRequest): Promise<TokenRefreshResponse> => {
    const response = await apiClient.post<TokenRefreshResponse>(
      API_ENDPOINTS.AUTH.REFRESH,
      data
    );
    return response.data;
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>(API_ENDPOINTS.AUTH.ME);
    return response.data;
  },
};
