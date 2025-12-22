// User & Auth Types
export enum UserRole {
  CHAUFFEUR = 'CHAUFFEUR',
  OPERATEUR_USINE = 'OPERATEUR_USINE',
  RESPONSABLE_LOGISTIQUE = 'RESPONSABLE_LOGISTIQUE',
  ADMIN = 'ADMIN',
}

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

// Palette Types
export enum PaletteType {
  B6 = 'B6',
  B12 = 'B12',
  B28 = 'B28',
}

export enum PaletteStatus {
  CREATION = 'CREATION',
  EN_STOCK = 'EN_STOCK',
  EN_ROUTE = 'EN_ROUTE',
  LIVREE = 'LIVREE',
  RETOUR = 'RETOUR',
  HORS_SERVICE = 'HORS_SERVICE',
}

export interface RFIDTag {
  id: string;
  tagNumber: string;
  label?: string;
  status: 'NOT_ASSIGNED' | 'ASSIGNED' | 'LOST' | 'DAMAGED';
  isActive: boolean;
  createdAt: string;
  assignedAt?: string;
}

export interface Palette {
  id: string;
  serialNumber: string;
  referenceCode?: string;
  rfidTagId?: string;
  rfidTag?: RFIDTag;
  type: PaletteType;
  capacity: number;
  currentFill: number;
  status: PaletteStatus;
  locationLatitude?: number;
  locationLongitude?: number;
  locationAddress?: string;
  notes?: string;
  currentExpeditionId?: string;
  currentPartnerId?: string;
  createdById: string;
  createdAt: string;
  updatedAt: string;
}

export interface PaletteCreate {
  rfidTagId: string;
  type: PaletteType;
  capacity: number;
  currentFill: number;
  referenceCode?: string;
  notes?: string;
}

// Expedition Types
export enum ExpeditionStatus {
  CREATION = 'CREATION',
  EN_ATTENTE = 'EN_ATTENTE',
  CREEE = 'CREEE',
  EN_TRANSIT = 'EN_TRANSIT',
  ARRIVEE = 'ARRIVEE',
  LIVREE = 'LIVREE',
  PROBLEME = 'PROBLEME',
  ANNULEE = 'ANNULEE',
}

export interface Expedition {
  id: string;
  referenceNumber: string;
  status: ExpeditionStatus;
  dateCreation: string;
  dateDeparture?: string;
  eta?: string;
  dateArrival?: string;
  dateDelivery?: string;
  transporter?: string;
  vehicleInfo?: string;
  destinationAddress: string;
  destinationContact?: string;
  destinationPhone?: string;
  notes?: string;
  otpCode?: string;
  otpExpiry?: string;
  paletteCount: number;
  grossisteId?: string;
  driverId?: string;
  createdById: string;
  palettes?: Palette[];
  createdAt: string;
  updatedAt: string;
}

// Notification Types
export enum NotificationType {
  NEW_EXPEDITION = 'NEW_EXPEDITION',
  STATUS_CHANGE = 'STATUS_CHANGE',
  REMINDER = 'REMINDER',
  ANOMALY = 'ANOMALY',
  SYSTEM = 'SYSTEM',
}

export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  data?: Record<string, any>;
  isRead: boolean;
  createdAt: string;
}

// Scan Types
export interface ScanResult {
  tagNumber: string;
  timestamp: number;
  latitude?: number;
  longitude?: number;
  success: boolean;
  error?: string;
}

// Signature Types
export interface Signature {
  type: 'GRAPHIC' | 'OTP' | 'HYBRID';
  graphicData?: string; // Base64 PNG
  otpCode?: string;
  timestamp: number;
  userId: string;
}

// Delivery Note (Bon de Livraison)
export interface DeliveryNote {
  id: string;
  expeditionId: string;
  expedition: Expedition;
  palettes: Palette[];
  signature?: Signature;
  pdfUrl?: string;
  qrCode?: string;
  createdAt: string;
}

// Offline Sync Types
export interface SyncQueueItem {
  id: string;
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  entity: 'PALETTE' | 'EXPEDITION' | 'SCAN' | 'SIGNATURE';
  data: any;
  timestamp: number;
  retryCount: number;
  status: 'PENDING' | 'SYNCING' | 'SUCCESS' | 'FAILED';
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Vehicle Types
export interface Vehicle {
  id: string;
  immatriculation: string;
  type?: string;
  brand?: string;
  model?: string;
  driverId?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// Error Types
export interface ApiError {
  message: string;
  code?: string;
  statusCode?: number;
  details?: any;
}

