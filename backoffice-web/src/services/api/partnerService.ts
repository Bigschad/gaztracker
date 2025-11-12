import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  Partner,
  PartnerCreate,
  PartnerUpdate,
  PaginatedResponse,
  PaginationParams,
} from '../../types';

interface PartnerListParams extends PaginationParams {
  type?: string;
  is_active?: boolean;
  search?: string;
}

export const partnerService = {
  // List partners
  list: async (params?: PartnerListParams): Promise<PaginatedResponse<Partner>> => {
    const response = await apiClient.get<PaginatedResponse<Partner>>(
      API_ENDPOINTS.PARTNERS.BASE,
      { params }
    );
    return response.data;
  },

  // Get partner by ID
  getById: async (id: string): Promise<Partner> => {
    const response = await apiClient.get<Partner>(
      API_ENDPOINTS.PARTNERS.BY_ID(id)
    );
    return response.data;
  },

  // Create partner
  create: async (data: PartnerCreate): Promise<Partner> => {
    const response = await apiClient.post<Partner>(
      API_ENDPOINTS.PARTNERS.BASE,
      data
    );
    return response.data;
  },

  // Update partner
  update: async (id: string, data: PartnerUpdate): Promise<Partner> => {
    const response = await apiClient.put<Partner>(
      API_ENDPOINTS.PARTNERS.BY_ID(id),
      data
    );
    return response.data;
  },

  // Delete partner
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.PARTNERS.BY_ID(id));
  },
};

