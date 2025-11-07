// Notification types matching backend schemas

export enum NotificationType {
  EXPEDITION_CREATED = 'EXPEDITION_CREATED',
  EXPEDITION_DEPARTED = 'EXPEDITION_DEPARTED',
  DELIVERY_CONFIRMATION = 'DELIVERY_CONFIRMATION',
  DELAY_ALERT = 'DELAY_ALERT',
  RFID_ANOMALY = 'RFID_ANOMALY',
  EXPEDITION_PROBLEM = 'EXPEDITION_PROBLEM',
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
  id: number;
  type: NotificationType;
  channel: NotificationChannel;
  recipient_email?: string;
  recipient_phone?: string;
  subject?: string;
  message: string;
  status: NotificationStatus;
  sent_at?: string;
  retry_count: number;
  error_message?: string;
  expedition_id?: number;
  palette_id?: number;
  user_id?: number;
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
  expedition_id?: number;
  palette_id?: number;
  user_id?: number;
}

export interface NotificationSendEmail {
  to_email: string;
  subject: string;
  body: string;
}

export interface NotificationSendSMS {
  to_phone: string;
  message: string;
}

export interface NotificationStatistics {
  total: number;
  by_status: Record<NotificationStatus, number>;
  by_type: Record<NotificationType, number>;
  by_channel: Record<NotificationChannel, number>;
  success_rate: number;
}
