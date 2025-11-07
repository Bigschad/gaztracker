import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  Expedition,
  ExpeditionCreate,
  ExpeditionUpdate,
  ExpeditionAssignPalettes,
  ExpeditionMarkDeparted,
  ExpeditionValidateDelivery,
  ExpeditionStatistics,
  PaginatedResponse,
  PaginationParams,
} from '../../types';

interface ExpeditionListParams extends PaginationParams {
  status?: string;
  driver_id?: number;
  grossiste_id?: number;
  search?: string;
}

export const expeditionService = {
  // List expeditions
  list: async (
    params?: ExpeditionListParams
  ): Promise<PaginatedResponse<Expedition>> => {
    const response = await apiClient.get<PaginatedResponse<Expedition>>(
      API_ENDPOINTS.EXPEDITIONS.BASE,
      { params }
    );
    return response.data;
  },

  // Get expedition by ID
  getById: async (id: number): Promise<Expedition> => {
    const response = await apiClient.get<Expedition>(
      API_ENDPOINTS.EXPEDITIONS.BY_ID(id)
    );
    return response.data;
  },

  // Create expedition
  create: async (data: ExpeditionCreate): Promise<Expedition> => {
    const response = await apiClient.post<Expedition>(
      API_ENDPOINTS.EXPEDITIONS.BASE,
      data
    );
    return response.data;
  },

  // Update expedition
  update: async (id: number, data: ExpeditionUpdate): Promise<Expedition> => {
    const response = await apiClient.put<Expedition>(
      API_ENDPOINTS.EXPEDITIONS.BY_ID(id),
      data
    );
    return response.data;
  },

  // Delete/Cancel expedition
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.EXPEDITIONS.BY_ID(id));
  },

  // Assign palettes
  assignPalettes: async (
    id: number,
    data: ExpeditionAssignPalettes
  ): Promise<Expedition> => {
    const response = await apiClient.post<Expedition>(
      API_ENDPOINTS.EXPEDITIONS.ASSIGN_PALETTES(id),
      data
    );
    return response.data;
  },

  // Mark as departed
  markAsDeparted: async (
    id: number,
    data: ExpeditionMarkDeparted
  ): Promise<Expedition> => {
    const response = await apiClient.post<Expedition>(
      API_ENDPOINTS.EXPEDITIONS.DEPART(id),
      data
    );
    return response.data;
  },

  // Validate delivery with OTP
  validateDelivery: async (
    id: number,
    data: ExpeditionValidateDelivery
  ): Promise<Expedition> => {
    const response = await apiClient.post<Expedition>(
      API_ENDPOINTS.EXPEDITIONS.VALIDATE(id),
      data
    );
    return response.data;
  },

  // Get statistics
  getStatistics: async (): Promise<ExpeditionStatistics> => {
    const response = await apiClient.get<ExpeditionStatistics>(
      API_ENDPOINTS.EXPEDITIONS.STATISTICS
    );
    return response.data;
  },
};
