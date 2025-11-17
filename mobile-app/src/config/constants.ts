// Session timeout (15 minutes)
export const SESSION_TIMEOUT = 15 * 60 * 1000; // 15 minutes en millisecondes

// Token refresh threshold (5 minutes before expiry)
export const TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000;

// Offline sync
export const SYNC_INTERVAL = 2 * 60 * 60 * 1000; // 2 heures
export const MAX_SYNC_RETRIES = 3;
export const SYNC_BATCH_SIZE = 50;

// RFID Scanner
export const RFID_SCAN_TIMEOUT = 10000; // 10 secondes
export const RFID_SCAN_INTERVAL = 1000; // 1 seconde entre les scans

// Cache
export const CACHE_EXPIRY = {
  EXPEDITIONS: 30 * 60 * 1000, // 30 minutes
  PALETTES: 60 * 60 * 1000, // 1 heure
  SETTINGS: 24 * 60 * 60 * 1000, // 24 heures
};

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

// File upload
export const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5 MB
export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

// GPS
export const GPS_UPDATE_INTERVAL = 5000; // 5 secondes
export const GPS_ACCURACY_THRESHOLD = 50; // 50 mètres

// Anomalies
export const DELAY_THRESHOLD = 30 * 60 * 1000; // 30 minutes
export const GEO_FENCE_RADIUS = 500; // 500 mètres

// Signature
export const SIGNATURE_QUALITY = 0.8; // Compression PNG
export const OTP_EXPIRY = 10 * 60 * 1000; // 10 minutes

// Storage
export const STORAGE_KEYS = {
  AUTH_TOKENS: '@gaztracker/auth_tokens',
  USER: '@gaztracker/user',
  SETTINGS: '@gaztracker/settings',
  SYNC_QUEUE: '@gaztracker/sync_queue',
  LAST_SYNC: '@gaztracker/last_sync',
  OFFLINE_MODE: '@gaztracker/offline_mode',
};

// Roles & Permissions
// Définir d'abord les permissions de base pour éviter les références circulaires
const CHAUFFEUR_PERMISSIONS = [
  'notifications:read',
  'expeditions:read',
  'expeditions:load',
  'expeditions:unload',
  'palettes:scan',
  'delivery_note:view',
  'delivery_note:sign',
];

const OPERATEUR_USINE_PERMISSIONS = [
  ...CHAUFFEUR_PERMISSIONS,
  'rfid_tags:create',
  'rfid_tags:read',
  'palettes:create',
  'palettes:update',
  'settings:read',
];

const RESPONSABLE_LOGISTIQUE_PERMISSIONS = [
  ...OPERATEUR_USINE_PERMISSIONS,
  'expeditions:create',
  'expeditions:update',
  'reports:view',
  'reports:export',
];

export const ROLE_PERMISSIONS = {
  CHAUFFEUR: CHAUFFEUR_PERMISSIONS,
  OPERATEUR_USINE: OPERATEUR_USINE_PERMISSIONS,
  RESPONSABLE_LOGISTIQUE: RESPONSABLE_LOGISTIQUE_PERMISSIONS,
  ADMIN: ['*'], // Tous les droits
};

// Palette Capacities
export const PALETTE_CAPACITIES = {
  B6: 12, // 12 bouteilles de 6kg
  B12: 8, // 8 bouteilles de 12kg
  B28: 4, // 4 bouteilles de 28kg
};

// Palette Weights (kg)
export const PALETTE_WEIGHTS = {
  B6: 72, // 12 * 6kg
  B12: 96, // 8 * 12kg
  B28: 112, // 4 * 28kg
};

