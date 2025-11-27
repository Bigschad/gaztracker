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
    BY_ID: (id: string) => `/api/v1/users/${id}`,
    STATISTICS: '/api/v1/users/statistics',
  },
  // Palettes
  PALETTES: {
    BASE: '/api/v1/palettes',
    BY_ID: (id: string) => `/api/v1/palettes/${id}`,
    SCAN: '/api/v1/palettes/scan',
    STATISTICS: '/api/v1/palettes/statistics',
    MOVEMENTS: (id: string) => `/api/v1/palettes/${id}/movements`,
  },
  // Expeditions - DEPRECATED (replaced by Bons d'Enlèvement and Bons de Réception Retour)
  // EXPEDITIONS: {
  //   BASE: '/api/v1/expeditions',
  //   BY_ID: (id: number) => `/api/v1/expeditions/${id}`,
  //   ASSIGN_PALETTES: (id: number) => `/api/v1/expeditions/${id}/palettes`,
  //   DEPART: (id: number) => `/api/v1/expeditions/${id}/depart`,
  //   VALIDATE: (id: number) => `/api/v1/expeditions/${id}/validate`,
  //   STATISTICS: '/api/v1/expeditions/statistics/overview',
  // },
  // Notifications
  NOTIFICATIONS: {
    BASE: '/api/v1/notifications',
    BY_ID: (id: string) => `/api/v1/notifications/${id}`,
    SEND_NOW: '/api/v1/notifications/send-now',
    SEND_EMAIL: '/api/v1/notifications/send-email',
    SEND_SMS: '/api/v1/notifications/send-sms',
    SEND: (id: string) => `/api/v1/notifications/${id}/send`,
    RETRY_FAILED: '/api/v1/notifications/retry/failed',
    STATISTICS: '/api/v1/notifications/statistics/overview',
    CHECK_DELAYS: '/api/v1/notifications/alerts/check-delays',
    CHECK_VALIDATIONS: '/api/v1/notifications/alerts/check-validations',
    RUN_ALL_CHECKS: '/api/v1/notifications/alerts/run-all',
  },
  // RFID Tags
  RFID_TAGS: {
    BASE: '/api/v1/rfid-tags',
    BY_ID: (id: string) => `/api/v1/rfid-tags/${id}`,
    BY_NUMBER: (tagNumber: string) => `/api/v1/rfid-tags/number/${tagNumber}`,
    MARK_LOST: (id: string) => `/api/v1/rfid-tags/${id}/mark-lost`,
    MARK_DAMAGED: (id: string) => `/api/v1/rfid-tags/${id}/mark-damaged`,
    STATISTICS: '/api/v1/rfid-tags/statistics/summary',
    BULK_IMPORT: '/api/v1/rfid-tags/bulk-import',
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
  // Partners
  PARTNERS: {
    BASE: '/api/v1/partners',
    BY_ID: (id: string) => `/api/v1/partners/${id}`,
  },
  // Contacts
  CONTACTS: {
    BASE: '/api/v1/contacts',
    BY_ID: (id: string) => `/api/v1/contacts/${id}`,
  },
  // Groupes
  GROUPES: {
    BASE: '/api/v1/groupes',
    BY_ID: (id: string) => `/api/v1/groupes/${id}`,
    COUNT: '/api/v1/groupes/count',
    ACTIVATE: (id: string) => `/api/v1/groupes/${id}/activate`,
    DEACTIVATE: (id: string) => `/api/v1/groupes/${id}/deactivate`,
  },
  // Centres Remplisseurs
  CENTRES_REMPLISSEURS: {
    BASE: '/api/v1/centres-remplisseurs',
    BY_ID: (id: string) => `/api/v1/centres-remplisseurs/${id}`,
    NEARBY: '/api/v1/centres-remplisseurs/nearby',
    ACTIVATE: (id: string) => `/api/v1/centres-remplisseurs/${id}/activate`,
    DEACTIVATE: (id: string) => `/api/v1/centres-remplisseurs/${id}/deactivate`,
  },
  // Dépôts
  DEPOTS: {
    BASE: '/api/v1/depots',
    BY_ID: (id: string) => `/api/v1/depots/${id}`,
    LOCATIONS: '/api/v1/depots/locations',
    NEARBY: '/api/v1/depots/nearby',
    ACTIVATE: (id: string) => `/api/v1/depots/${id}/activate`,
    DEACTIVATE: (id: string) => `/api/v1/depots/${id}/deactivate`,
    SET_MAIN: (id: string) => `/api/v1/depots/${id}/set-main`,
  },
  // Bons d'Enlèvement
  BONS_ENLEVEMENT: {
    BASE: '/api/v1/bons-enlevement',
    BY_ID: (id: string) => `/api/v1/bons-enlevement/${id}`,
    VALIDER: (id: string) => `/api/v1/bons-enlevement/${id}/valider`,
    START_CHARGEMENT: (id: string) => `/api/v1/bons-enlevement/${id}/start-chargement`,
    DEPART: (id: string) => `/api/v1/bons-enlevement/${id}/depart`,
    START_LIVRAISON: (id: string) => `/api/v1/bons-enlevement/${id}/start-livraison`,
    TERMINER: (id: string) => `/api/v1/bons-enlevement/${id}/terminer`,
    ANNULER: (id: string) => `/api/v1/bons-enlevement/${id}/annuler`,
  },
  // Bons de Réception Retour
  BONS_RECEPTION_RETOUR: {
    BASE: '/api/v1/bons-reception-retour',
    BY_ID: (id: string) => `/api/v1/bons-reception-retour/${id}`,
    DEPART: (id: string) => `/api/v1/bons-reception-retour/${id}/depart`,
    ARRIVEE: (id: string) => `/api/v1/bons-reception-retour/${id}/arrivee`,
    CONTROLE: (id: string) => `/api/v1/bons-reception-retour/${id}/controle`,
    VALIDER: (id: string) => `/api/v1/bons-reception-retour/${id}/valider`,
    REFUSER: (id: string) => `/api/v1/bons-reception-retour/${id}/refuser`,
  },
  // Uploads
  UPLOADS: {
    LOGOS: '/api/v1/uploads/logos',
    LOGO_BY_NAME: (filename: string) => `/api/v1/uploads/logos/${filename}`,
  },
};
