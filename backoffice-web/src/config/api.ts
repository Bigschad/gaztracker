// API configuration

export const API_CONFIG = {
  // Use relative URL to leverage nginx proxy in production
  // In dev mode, you can set VITE_API_URL to http://localhost:8000
  BASE_URL: import.meta.env.VITE_API_URL || '',
  API_VERSION: 'v1',
  TIMEOUT: 30000, // 30 seconds
};

export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    LOGOUT: '/api/v1/auth/logout',
    REFRESH: '/api/v1/auth/refresh',
    ME: '/api/v1/auth/me',
  },
  // Users
  USERS: {
    BASE: '/api/v1/users',
    BY_ID: (id: number) => `/api/v1/users/${id}`,
    STATISTICS: '/api/v1/users/statistics',
  },
  // Palettes
  PALETTES: {
    BASE: '/api/v1/palettes',
    BY_ID: (id: number) => `/api/v1/palettes/${id}`,
    SCAN: '/api/v1/palettes/scan',
    STATISTICS: '/api/v1/palettes/statistics',
    MOVEMENTS: (id: number) => `/api/v1/palettes/${id}/movements`,
  },
  // Expeditions
  EXPEDITIONS: {
    BASE: '/api/v1/expeditions',
    BY_ID: (id: number) => `/api/v1/expeditions/${id}`,
    ASSIGN_PALETTES: (id: number) => `/api/v1/expeditions/${id}/palettes`,
    DEPART: (id: number) => `/api/v1/expeditions/${id}/depart`,
    VALIDATE: (id: number) => `/api/v1/expeditions/${id}/validate`,
    STATISTICS: '/api/v1/expeditions/statistics/overview',
  },
  // Notifications
  NOTIFICATIONS: {
    BASE: '/api/v1/notifications',
    BY_ID: (id: number) => `/api/v1/notifications/${id}`,
    SEND_NOW: '/api/v1/notifications/send-now',
    SEND_EMAIL: '/api/v1/notifications/send-email',
    SEND_SMS: '/api/v1/notifications/send-sms',
    SEND: (id: number) => `/api/v1/notifications/${id}/send`,
    RETRY_FAILED: '/api/v1/notifications/retry/failed',
    STATISTICS: '/api/v1/notifications/statistics/overview',
    CHECK_DELAYS: '/api/v1/notifications/alerts/check-delays',
    CHECK_VALIDATIONS: '/api/v1/notifications/alerts/check-validations',
    RUN_ALL_CHECKS: '/api/v1/notifications/alerts/run-all',
  },
  // Reports
  REPORTS: {
    PALETTES_STATS: '/api/v1/reports/palettes/statistics',
    PALETTES_TREND: '/api/v1/reports/palettes/utilization-trend',
    PALETTES_DISTRIBUTION: '/api/v1/reports/palettes/distribution',
    EXPEDITIONS_STATS: '/api/v1/reports/expeditions/statistics',
    EXPEDITIONS_TREND: '/api/v1/reports/expeditions/trend',
    TOP_DESTINATIONS: '/api/v1/reports/expeditions/top-destinations',
    PERFORMANCE: '/api/v1/reports/performance',
    DASHBOARD: '/api/v1/reports/dashboard/overview',
    USER_PERFORMANCE: '/api/v1/reports/users/performance',
    EXPORT_EXPEDITIONS: '/api/v1/reports/export/expeditions',
    EXPORT_PALETTES: '/api/v1/reports/export/palettes',
    QUICK_STATS: '/api/v1/reports/quick-stats',
  },
};
