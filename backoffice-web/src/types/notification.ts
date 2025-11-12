// Notification types matching backend schemas

export enum NotificationType {
  ALERTE_RETARD = 'ALERTE_RETARD',
  ANOMALIE_RFID = 'ANOMALIE_RFID',
  DIVERGENCE_RECEPTION = 'DIVERGENCE_RECEPTION',
  CONFIRMATION_LIVRAISON = 'CONFIRMATION_LIVRAISON',
  EXPEDITION_CREEE = 'EXPEDITION_CREEE',
  EXPEDITION_DEPART = 'EXPEDITION_DEPART',
  EXPEDITION_ARRIVEE = 'EXPEDITION_ARRIVEE',
  PROBLEME_EXPEDITION = 'PROBLEME_EXPEDITION',
  VALIDATION_REQUISE = 'VALIDATION_REQUISE',
  RETOUR_PALETTE = 'RETOUR_PALETTE',
}

export enum NotificationChannel {
  EMAIL = 'EMAIL',
  SMS = 'SMS',
  BOTH = 'BOTH',
}

export enum NotificationStatus {
  PENDING = 'PENDING',
  SENT = 'SENT',
  FAILED = 'FAILED',
  RETRYING = 'RETRYING',
}

export interface Notification {
  id: string; // UUID
  type: NotificationType;
  channel: NotificationChannel;
  recipient_email?: string;
  recipient_phone?: string;
  subject?: string;
  message: string;
  status: NotificationStatus;
  sent_at?: string;
  retry_count: string; // Backend uses string
  error_message?: string;
  expedition_id?: string; // UUID
  palette_id?: string; // UUID
  user_id?: string; // UUID
  created_at: string;
  updated_at: string;
}

export interface NotificationCreate {
  type: NotificationType;
  channel: NotificationChannel;
  recipient_email?: string;
  recipient_phone?: string;
  subject?: string;
  message: string;
  expedition_id?: string; // UUID
  palette_id?: string; // UUID
  user_id?: string; // UUID
}

export interface NotificationSendEmail {
  to_email: string;
  subject: string;
  body: string;
  is_html?: boolean;
}

export interface NotificationSendSMS {
  to_phone: string;
  message: string;
}

export interface NotificationStatistics {
  total_notifications: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_channel: Record<string, number>;
  success_rate: number;
  failed_count: number;
}
