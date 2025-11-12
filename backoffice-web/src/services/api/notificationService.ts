import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  Notification,
  NotificationCreate,
  NotificationSendEmail,
  NotificationSendSMS,
  NotificationStatistics,
  NotificationStatus,
  NotificationType,
  NotificationChannel,
} from '../../types';

export interface NotificationListParams {
  status?: NotificationStatus;
  type?: NotificationType;
  channel?: NotificationChannel;
  page?: number;
  page_size?: number;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const notificationService = {
  // List notifications with filters
  list: async (params?: NotificationListParams): Promise<NotificationListResponse> => {
    const response = await apiClient.get<NotificationListResponse>(
      API_ENDPOINTS.NOTIFICATIONS.BASE,
      { params }
    );
    return response.data;
  },

  // Get notification by ID
  getById: async (id: string): Promise<Notification> => {
    const response = await apiClient.get<Notification>(
      API_ENDPOINTS.NOTIFICATIONS.BY_ID(id)
    );
    return response.data;
  },

  // Create notification
  create: async (data: NotificationCreate): Promise<Notification> => {
    const response = await apiClient.post<Notification>(
      API_ENDPOINTS.NOTIFICATIONS.BASE,
      data
    );
    return response.data;
  },

  // Create and send notification immediately
  sendNow: async (data: NotificationCreate): Promise<Notification> => {
    const response = await apiClient.post<Notification>(
      API_ENDPOINTS.NOTIFICATIONS.SEND_NOW,
      data
    );
    return response.data;
  },

  // Send a pending notification
  send: async (id: string): Promise<Notification> => {
    const response = await apiClient.post<Notification>(
      API_ENDPOINTS.NOTIFICATIONS.SEND(id)
    );
    return response.data;
  },

  // Send standalone email
  sendEmail: async (data: NotificationSendEmail): Promise<void> => {
    await apiClient.post(API_ENDPOINTS.NOTIFICATIONS.SEND_EMAIL, data);
  },

  // Send standalone SMS
  sendSMS: async (data: NotificationSendSMS): Promise<void> => {
    await apiClient.post(API_ENDPOINTS.NOTIFICATIONS.SEND_SMS, data);
  },

  // Retry failed notifications
  retryFailed: async (maxRetries?: number): Promise<{ retried: number }> => {
    const response = await apiClient.post<{ retried: number }>(
      API_ENDPOINTS.NOTIFICATIONS.RETRY_FAILED,
      { max_retries: maxRetries }
    );
    return response.data;
  },

  // Get notification statistics
  getStatistics: async (): Promise<NotificationStatistics> => {
    const response = await apiClient.get<NotificationStatistics>(
      API_ENDPOINTS.NOTIFICATIONS.STATISTICS
    );
    return response.data;
  },

  // Check delayed expeditions
  checkDelays: async (): Promise<{ checked: number; notifications_sent: number }> => {
    const response = await apiClient.post<{ checked: number; notifications_sent: number }>(
      API_ENDPOINTS.NOTIFICATIONS.CHECK_DELAYS
    );
    return response.data;
  },

  // Check pending validations
  checkValidations: async (): Promise<{ checked: number; notifications_sent: number }> => {
    const response = await apiClient.post<{ checked: number; notifications_sent: number }>(
      API_ENDPOINTS.NOTIFICATIONS.CHECK_VALIDATIONS
    );
    return response.data;
  },

  // Run all alert checks
  runAllChecks: async (): Promise<{
    delays: { checked: number; notifications_sent: number };
    validations: { checked: number; notifications_sent: number };
  }> => {
    const response = await apiClient.post<{
      delays: { checked: number; notifications_sent: number };
      validations: { checked: number; notifications_sent: number };
    }>(API_ENDPOINTS.NOTIFICATIONS.RUN_ALL_CHECKS);
    return response.data;
  },
};

