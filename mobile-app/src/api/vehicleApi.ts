import axiosClient from './axiosClient';
import { API_ENDPOINTS } from '../config/apiConfig';
import { Vehicle, PaginatedResponse } from '../types';

export interface VehicleCreate {
  immatriculation: string;
  type?: string;
  brand?: string;
  model?: string;
}

export const vehicleApi = {
  list: async (params?: {
    page?: number;
    pageSize?: number;
    driverId?: string;
    isActive?: boolean;
  }): Promise<PaginatedResponse<Vehicle>> => {
    const response = await axiosClient.get(API_ENDPOINTS.VEHICLES.LIST, { params });
    return response.data;
  },

  create: async (data: VehicleCreate): Promise<Vehicle> => {
    const response = await axiosClient.post(API_ENDPOINTS.VEHICLES.CREATE, data);
    return response.data.data;
  },

  getById: async (id: string): Promise<Vehicle> => {
    const response = await axiosClient.get(API_ENDPOINTS.VEHICLES.GET_BY_ID(id));
    return response.data.data;
  },

  update: async (id: string, data: Partial<VehicleCreate>): Promise<Vehicle> => {
    const response = await axiosClient.put(API_ENDPOINTS.VEHICLES.UPDATE(id), data);
    return response.data.data;
  },

  delete: async (id: string): Promise<void> => {
    await axiosClient.delete(API_ENDPOINTS.VEHICLES.DELETE(id));
  },
};
