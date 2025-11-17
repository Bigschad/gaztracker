import axiosClient from './axiosClient';
import { API_ENDPOINTS } from '../config/apiConfig';
import { Palette, PaletteCreate, PaginatedResponse } from '../types';

export interface PaletteScanRequest {
  rfidTag: string;
  latitude?: number;
  longitude?: number;
  notes?: string;
}

export const paletteApi = {
  list: async (params?: {
    page?: number;
    pageSize?: number;
    type?: string;
    status?: string;
  }): Promise<PaginatedResponse<Palette>> => {
    const response = await axiosClient.get(API_ENDPOINTS.PALETTES.LIST, { params });
    return response.data;
  },

  create: async (data: PaletteCreate): Promise<Palette> => {
    const response = await axiosClient.post(API_ENDPOINTS.PALETTES.CREATE, data);
    return response.data.data;
  },

  getById: async (id: string): Promise<Palette> => {
    const response = await axiosClient.get(API_ENDPOINTS.PALETTES.GET_BY_ID(id));
    return response.data.data;
  },

  getByRfid: async (tagNumber: string): Promise<Palette> => {
    const response = await axiosClient.get(API_ENDPOINTS.PALETTES.GET_BY_RFID(tagNumber));
    return response.data.data;
  },

  scan: async (data: PaletteScanRequest): Promise<Palette> => {
    const response = await axiosClient.post(API_ENDPOINTS.PALETTES.SCAN, data);
    return response.data.data;
  },
};

