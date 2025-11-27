import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  Depot,
  DepotList,
  DepotDetail,
  DepotLocation,
  DepotCreate,
  DepotUpdate,
} from '../../types';

interface DepotListParams {
  skip?: number;
  limit?: number;
  partner_id?: string;
  is_active?: boolean;
  is_main_depot?: boolean;
  city?: string;
  search?: string;
}

interface NearbyParams {
  latitude: number;
  longitude: number;
  radius_km?: number;
  is_active?: boolean;
}

export const depotService = {
  // List depots
  list: async (params?: DepotListParams): Promise<DepotList[]> => {
    const response = await apiClient.get<DepotList[]>(
      API_ENDPOINTS.DEPOTS.BASE,
      { params }
    );
    return response.data;
  },

  // Get depot locations (for maps)
  getLocations: async (is_active: boolean = true): Promise<DepotLocation[]> => {
    const response = await apiClient.get<DepotLocation[]>(
      API_ENDPOINTS.DEPOTS.LOCATIONS,
      { params: { is_active } }
    );
    return response.data;
  },

  // Get nearby depots
  getNearby: async (params: NearbyParams): Promise<Depot[]> => {
    const response = await apiClient.get<Depot[]>(
      API_ENDPOINTS.DEPOTS.NEARBY,
      { params }
    );
    return response.data;
  },

  // Get depot by ID
  getById: async (id: string): Promise<DepotDetail> => {
    const response = await apiClient.get<DepotDetail>(
      API_ENDPOINTS.DEPOTS.BY_ID(id)
    );
    return response.data;
  },

  // Create depot
  create: async (data: DepotCreate): Promise<Depot> => {
    const response = await apiClient.post<Depot>(
      API_ENDPOINTS.DEPOTS.BASE,
      data
    );
    return response.data;
  },

  // Update depot
  update: async (id: string, data: DepotUpdate): Promise<Depot> => {
    const response = await apiClient.patch<Depot>(
      API_ENDPOINTS.DEPOTS.BY_ID(id),
      data
    );
    return response.data;
  },

  // Delete depot
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.DEPOTS.BY_ID(id));
  },

  // Activate depot
  activate: async (id: string): Promise<Depot> => {
    const response = await apiClient.post<Depot>(
      API_ENDPOINTS.DEPOTS.ACTIVATE(id)
    );
    return response.data;
  },

  // Deactivate depot
  deactivate: async (id: string): Promise<Depot> => {
    const response = await apiClient.post<Depot>(
      API_ENDPOINTS.DEPOTS.DEACTIVATE(id)
    );
    return response.data;
  },

  // Set as main depot
  setAsMain: async (id: string): Promise<Depot> => {
    const response = await apiClient.post<Depot>(
      API_ENDPOINTS.DEPOTS.SET_MAIN(id)
    );
    return response.data;
  },
};

