import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  CentreRemplisseur,
  CentreRemplisseurList,
  CentreRemplisseurDetail,
  CentreRemplisseurCreate,
  CentreRemplisseurUpdate,
} from '../../types';

interface CentreRemplisseurListParams {
  skip?: number;
  limit?: number;
  partner_id?: string;
  is_active?: boolean;
  city?: string;
  search?: string;
}

interface NearbyParams {
  latitude: number;
  longitude: number;
  radius_km?: number;
}

export const centreRemplisseurService = {
  // List centres remplisseurs
  list: async (params?: CentreRemplisseurListParams): Promise<CentreRemplisseurList[]> => {
    const response = await apiClient.get<CentreRemplisseurList[]>(
      API_ENDPOINTS.CENTRES_REMPLISSEURS.BASE,
      { params }
    );
    return response.data;
  },

  // Get nearby centres
  getNearby: async (params: NearbyParams): Promise<CentreRemplisseur[]> => {
    const response = await apiClient.get<CentreRemplisseur[]>(
      API_ENDPOINTS.CENTRES_REMPLISSEURS.NEARBY,
      { params }
    );
    return response.data;
  },

  // Get centre by ID
  getById: async (id: string): Promise<CentreRemplisseurDetail> => {
    const response = await apiClient.get<CentreRemplisseurDetail>(
      API_ENDPOINTS.CENTRES_REMPLISSEURS.BY_ID(id)
    );
    return response.data;
  },

  // Create centre
  create: async (data: CentreRemplisseurCreate): Promise<CentreRemplisseur> => {
    const response = await apiClient.post<CentreRemplisseur>(
      API_ENDPOINTS.CENTRES_REMPLISSEURS.BASE,
      data
    );
    return response.data;
  },

  // Update centre
  update: async (id: string, data: CentreRemplisseurUpdate): Promise<CentreRemplisseur> => {
    const response = await apiClient.patch<CentreRemplisseur>(
      API_ENDPOINTS.CENTRES_REMPLISSEURS.BY_ID(id),
      data
    );
    return response.data;
  },

  // Delete centre
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.CENTRES_REMPLISSEURS.BY_ID(id));
  },

  // Activate centre
  activate: async (id: string): Promise<CentreRemplisseur> => {
    const response = await apiClient.post<CentreRemplisseur>(
      API_ENDPOINTS.CENTRES_REMPLISSEURS.ACTIVATE(id)
    );
    return response.data;
  },

  // Deactivate centre
  deactivate: async (id: string): Promise<CentreRemplisseur> => {
    const response = await apiClient.post<CentreRemplisseur>(
      API_ENDPOINTS.CENTRES_REMPLISSEURS.DEACTIVATE(id)
    );
    return response.data;
  },
};

