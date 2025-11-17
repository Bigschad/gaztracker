import Constants from 'expo-constants';
import { Platform } from 'react-native';

const isDev = __DEV__;
const isEmulator = Constants.executionEnvironment === 'standalone';

// Get API URL from environment variable or use defaults
// You can set apiUrl in app.json extra section or via environment variables
const getApiBaseUrl = (): string => {
  // Check for API URL in app.json extra section (recommended)
  const extraConfig = Constants.expoConfig?.extra as { apiUrl?: string } | undefined;
  if (extraConfig?.apiUrl) {
    let apiUrl = extraConfig.apiUrl;
    // Ensure the URL has a protocol
    if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
      apiUrl = `http://${apiUrl}`;
    }
    return apiUrl;
  }
  
  // Fallback to default based on environment
  if (isDev) {
    // For web platform, use localhost
    if (Platform.OS === 'web') {
      return 'http://localhost:8000';
    }
    // For Android Emulator
    if (isEmulator) {
      return 'http://10.0.2.2:8000';
    }
    // Default to your local IP - update this if your IP changes
    // You can also set it in app.json extra.apiUrl
    return 'http://192.168.1.4:8000'; // Local development (physical device)
  }
  
  return 'https://api.gaztracker.com'; // Production
};

export const API_CONFIG = {
  baseUrl: getApiBaseUrl(),
  apiPrefix: '/api/v1',
  timeout: 30000, // 30 secondes
};

export const getApiUrl = (endpoint: string = '') => {
  return `${API_CONFIG.baseUrl}${API_CONFIG.apiPrefix}${endpoint}`;
};

// Endpoints
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/auth/login',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
  },
  // RFID Tags
  RFID_TAGS: {
    LIST: '/rfid-tags',
    CREATE: '/rfid-tags',
    GET_BY_NUMBER: (tagNumber: string) => `/rfid-tags/number/${tagNumber}`,
    GET_BY_ID: (id: string) => `/rfid-tags/${id}`,
    UPDATE: (id: string) => `/rfid-tags/${id}`,
  },
  // Palettes
  PALETTES: {
    LIST: '/palettes',
    CREATE: '/palettes',
    GET_BY_ID: (id: string) => `/palettes/${id}`,
    GET_BY_RFID: (tagNumber: string) => `/palettes/rfid/${tagNumber}`,
    UPDATE: (id: string) => `/palettes/${id}`,
    SCAN: '/palettes/scan',
  },
  // Expeditions
  EXPEDITIONS: {
    LIST: '/expeditions',
    CREATE: '/expeditions',
    GET_BY_ID: (id: string) => `/expeditions/${id}`,
    UPDATE: (id: string) => `/expeditions/${id}`,
    ASSIGN_PALETTES: (id: string) => `/expeditions/${id}/palettes`,
    DEPART: (id: string) => `/expeditions/${id}/depart`,
    VALIDATE: (id: string) => `/expeditions/${id}/validate`,
  },
  // Notifications
  NOTIFICATIONS: {
    LIST: '/notifications',
    MARK_READ: (id: string) => `/notifications/${id}/read`,
    MARK_ALL_READ: '/notifications/read-all',
  },
};

