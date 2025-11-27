import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  Groupe,
  GroupeList,
  GroupeDetail,
  GroupeCreate,
  GroupeUpdate,
} from '../../types';

interface GroupeListParams {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  search?: string;
}

export const groupeService = {
  // List groupes
  list: async (params?: GroupeListParams): Promise<GroupeList[]> => {
    const response = await apiClient.get<GroupeList[]>(
      API_ENDPOINTS.GROUPES.BASE,
      { params }
    );
    return response.data;
  },

  // Count groupes
  count: async (is_active?: boolean): Promise<{ count: number }> => {
    const response = await apiClient.get<{ count: number }>(
      API_ENDPOINTS.GROUPES.COUNT,
      { params: { is_active } }
    );
    return response.data;
  },

  // Get groupe by ID
  getById: async (id: string): Promise<GroupeDetail> => {
    const response = await apiClient.get<GroupeDetail>(
      API_ENDPOINTS.GROUPES.BY_ID(id)
    );
    return response.data;
  },

  // Create groupe
  create: async (data: GroupeCreate): Promise<Groupe> => {
    const response = await apiClient.post<Groupe>(
      API_ENDPOINTS.GROUPES.BASE,
      data
    );
    return response.data;
  },

  // Update groupe
  update: async (id: string, data: GroupeUpdate): Promise<Groupe> => {
    const response = await apiClient.patch<Groupe>(
      API_ENDPOINTS.GROUPES.BY_ID(id),
      data
    );
    return response.data;
  },

  // Delete groupe
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.GROUPES.BY_ID(id));
  },

  // Activate groupe
  activate: async (id: string): Promise<Groupe> => {
    const response = await apiClient.post<Groupe>(
      API_ENDPOINTS.GROUPES.ACTIVATE(id)
    );
    return response.data;
  },

  // Deactivate groupe
  deactivate: async (id: string): Promise<Groupe> => {
    const response = await apiClient.post<Groupe>(
      API_ENDPOINTS.GROUPES.DEACTIVATE(id)
    );
    return response.data;
  },
};

