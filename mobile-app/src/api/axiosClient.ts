import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { Platform } from 'react-native';
import { API_CONFIG, getApiUrl } from '../config/apiConfig';
import { AuthTokens } from '../types';
import { STORAGE_KEYS } from '../config/constants';

// Import conditionnel SecureStore
let SecureStore: any;
if (Platform.OS === 'web') {
  SecureStore = require('../utils/secureStore.web').SecureStore;
} else {
  SecureStore = require('expo-secure-store');
}

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

const axiosClient: AxiosInstance = axios.create({
  baseURL: getApiUrl(),
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Ajouter le token JWT
axiosClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      const tokensJson = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_TOKENS);
      if (tokensJson) {
        const tokens: AuthTokens = JSON.parse(tokensJson);
        if (tokens.accessToken && config.headers) {
          config.headers.Authorization = `Bearer ${tokens.accessToken}`;
          console.log('[Axios] Token added to request:', {
            url: config.url,
            hasToken: !!tokens.accessToken,
            tokenPreview: tokens.accessToken.substring(0, 20) + '...',
          });
        } else {
          console.warn('[Axios] No access token found in stored tokens');
        }
      } else {
        console.warn('[Axios] No tokens found in SecureStore for request:', config.url);
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Gérer le refresh token
axiosClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Si erreur 401 et pas déjà en train de refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Mettre en queue la requête
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return axiosClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const tokensJson = await SecureStore.getItemAsync(STORAGE_KEYS.AUTH_TOKENS);
        if (!tokensJson) {
          throw new Error('No refresh token');
        }

        const tokens: AuthTokens = JSON.parse(tokensJson);
        if (!tokens.refreshToken) {
          throw new Error('No refresh token');
        }

        // Appel API pour refresh
        const response = await axios.post(getApiUrl('/auth/refresh'), {
          refresh_token: tokens.refreshToken,
        });

        const data = response.data;
        // expires_in est en secondes, on le convertit en timestamp (millisecondes)
        const expiresInSeconds = data.expires_in || 30 * 60; // 30 minutes par défaut en secondes
        const expiresInTimestamp = Date.now() + (expiresInSeconds * 1000);
        
        const newTokens: AuthTokens = {
          accessToken: data.access_token,
          refreshToken: tokens.refreshToken, // Le refresh token reste le même
          expiresIn: expiresInTimestamp, // Timestamp d'expiration
        };
        await SecureStore.setItemAsync(STORAGE_KEYS.AUTH_TOKENS, JSON.stringify(newTokens));

        processQueue(null, newTokens.accessToken);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newTokens.accessToken}`;
        }

        isRefreshing = false;
        return axiosClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;

        // Supprimer les tokens et rediriger vers login
        await SecureStore.deleteItemAsync(STORAGE_KEYS.AUTH_TOKENS);
        await SecureStore.deleteItemAsync(STORAGE_KEYS.USER);

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosClient;

