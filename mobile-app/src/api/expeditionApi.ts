import axiosClient from './axiosClient';
import { API_ENDPOINTS } from '../config/apiConfig';
import { Expedition, PaginatedResponse } from '../types';

export interface ExpeditionCreate {
  referenceNumber: string;
  destinationAddress: string;
  destinationContact?: string;
  destinationPhone?: string;
  transporter?: string;
  vehicleInfo?: string;
  notes?: string;
  paletteIds?: string[];
}

export const expeditionApi = {
  list: async (params?: {
    page?: number;
    pageSize?: number;
    status?: string;
    driverId?: string;
  }): Promise<PaginatedResponse<Expedition>> => {
    const response = await axiosClient.get(API_ENDPOINTS.EXPEDITIONS.LIST, { params });
    return response.data;
  },

  getById: async (id: string): Promise<Expedition> => {
    const response = await axiosClient.get(API_ENDPOINTS.EXPEDITIONS.GET_BY_ID(id));
    return response.data.data;
  },

  assignPalettes: async (expeditionId: string, paletteIds: string[]): Promise<Expedition> => {
    const response = await axiosClient.post(
      API_ENDPOINTS.EXPEDITIONS.ASSIGN_PALETTES(expeditionId),
      paletteIds
    );
    return response.data.data;
  },
};

