import axiosClient from './axiosClient';
import { API_ENDPOINTS } from '../config/apiConfig';
import { LoginCredentials, User, AuthTokens } from '../types';

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<{ user: User; tokens: AuthTokens }> => {
    const response = await axiosClient.post(API_ENDPOINTS.AUTH.LOGIN, credentials);
    // La réponse de l'API contient directement les champs access_token, refresh_token, etc.
    const data = response.data;
    console.log('[AuthAPI] Login response received:', {
      hasAccessToken: !!data.access_token,
      hasRefreshToken: !!data.refresh_token,
      expiresIn: data.expires_in,
      hasUser: !!data.user,
    });
    
    // expires_in est en secondes, on le convertit en timestamp (millisecondes)
    const expiresInSeconds = data.expires_in || 30 * 60; // 30 minutes par défaut en secondes
    const expiresInTimestamp = Date.now() + (expiresInSeconds * 1000);
    
    // Mapper les données utilisateur de snake_case à camelCase
    const userData = data.user;
    const user: User = {
      id: userData.id,
      email: userData.email,
      firstName: userData.first_name,
      lastName: userData.last_name,
      role: userData.role,
      isActive: userData.is_active,
      createdAt: userData.created_at,
      updatedAt: userData.updated_at,
    };
    
    const tokens: AuthTokens = {
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
      expiresIn: expiresInTimestamp, // Timestamp d'expiration
    };
    
    console.log('[AuthAPI] Tokens prepared:', {
      hasAccessToken: !!tokens.accessToken,
      hasRefreshToken: !!tokens.refreshToken,
      expiresIn: tokens.expiresIn,
      expiresInDate: new Date(tokens.expiresIn).toISOString(),
    });
    
    return {
      user,
      tokens,
    };
  },

  refreshToken: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await axiosClient.post(API_ENDPOINTS.AUTH.REFRESH, { refresh_token: refreshToken });
    const data = response.data;
    // expires_in est en secondes, on le convertit en timestamp (millisecondes)
    const expiresInSeconds = data.expires_in || 30 * 60; // 30 minutes par défaut en secondes
    const expiresInTimestamp = Date.now() + (expiresInSeconds * 1000);
    
    return {
      accessToken: data.access_token,
      refreshToken: refreshToken, // Le refresh token reste le même
      expiresIn: expiresInTimestamp, // Timestamp d'expiration
    };
  },

  logout: async (): Promise<void> => {
    await axiosClient.post(API_ENDPOINTS.AUTH.LOGOUT);
  },

  getMe: async (): Promise<User> => {
    const response = await axiosClient.get(API_ENDPOINTS.AUTH.ME);
    const userData = response.data.data || response.data;
    // Mapper les données utilisateur de snake_case à camelCase
    return {
      id: userData.id,
      email: userData.email,
      firstName: userData.first_name,
      lastName: userData.last_name,
      role: userData.role,
      isActive: userData.is_active,
      createdAt: userData.created_at,
      updatedAt: userData.updated_at,
    };
  },
};

