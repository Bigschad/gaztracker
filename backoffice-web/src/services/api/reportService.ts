import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  DashboardOverview,
  PerformanceReport,
  TopDestination,
  UserPerformance,
  ExportRequest,
  DateRange,
} from '../../types';

export const reportService = {
  // Get dashboard overview
  getDashboard: async (): Promise<DashboardOverview> => {
    const response = await apiClient.get<DashboardOverview>(
      API_ENDPOINTS.REPORTS.DASHBOARD
    );
    return response.data;
  },

  // Get performance report
  getPerformanceReport: async (params?: DateRange): Promise<PerformanceReport> => {
    const response = await apiClient.get<PerformanceReport>(
      API_ENDPOINTS.REPORTS.PERFORMANCE,
      { params }
    );
    return response.data;
  },

  // Get top destinations
  getTopDestinations: async (limit?: number): Promise<TopDestination[]> => {
    const response = await apiClient.get<TopDestination[]>(
      API_ENDPOINTS.REPORTS.TOP_DESTINATIONS,
      { params: { limit } }
    );
    return response.data;
  },

  // Get user performance
  getUserPerformance: async (params?: DateRange): Promise<UserPerformance[]> => {
    const response = await apiClient.get<UserPerformance[]>(
      API_ENDPOINTS.REPORTS.USER_PERFORMANCE,
      { params }
    );
    return response.data;
  },

  // Export expeditions
  exportExpeditions: async (request: ExportRequest): Promise<Blob> => {
    const response = await apiClient.get(API_ENDPOINTS.REPORTS.EXPORT_EXPEDITIONS, {
      params: request,
      responseType: 'blob',
    });
    return response.data;
  },

  // Export palettes
  exportPalettes: async (request: ExportRequest): Promise<Blob> => {
    const response = await apiClient.get(API_ENDPOINTS.REPORTS.EXPORT_PALETTES, {
      params: request,
      responseType: 'blob',
    });
    return response.data;
  },
};
