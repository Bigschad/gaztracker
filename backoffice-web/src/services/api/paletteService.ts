import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  Palette,
  PaletteCreate,
  PaletteUpdate,
  PaletteScan,
  PaletteStatistics,
  PaletteMovement,
  PaginatedResponse,
  PaginationParams,
} from '../../types';

interface PaletteListParams extends PaginationParams {
  status?: string;
  palette_type?: string;
  search?: string;
}

export const paletteService = {
  // List palettes
  list: async (params?: PaletteListParams): Promise<PaginatedResponse<Palette>> => {
    const response = await apiClient.get<PaginatedResponse<Palette>>(
      API_ENDPOINTS.PALETTES.BASE,
      { params }
    );
    return response.data;
  },

  // Get palette by ID
  getById: async (id: number): Promise<Palette> => {
    const response = await apiClient.get<Palette>(
      API_ENDPOINTS.PALETTES.BY_ID(id)
    );
    return response.data;
  },

  // Create palette
  create: async (data: PaletteCreate): Promise<Palette> => {
    const response = await apiClient.post<Palette>(
      API_ENDPOINTS.PALETTES.BASE,
      data
    );
    return response.data;
  },

  // Update palette
  update: async (id: number, data: PaletteUpdate): Promise<Palette> => {
    const response = await apiClient.put<Palette>(
      API_ENDPOINTS.PALETTES.BY_ID(id),
      data
    );
    return response.data;
  },

  // Delete palette
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.PALETTES.BY_ID(id));
  },

  // Scan palette
  scan: async (data: PaletteScan): Promise<Palette> => {
    const response = await apiClient.post<Palette>(
      API_ENDPOINTS.PALETTES.SCAN,
      data
    );
    return response.data;
  },

  // Get statistics
  getStatistics: async (): Promise<PaletteStatistics> => {
    const response = await apiClient.get<PaletteStatistics>(
      API_ENDPOINTS.PALETTES.STATISTICS
    );
    return response.data;
  },

  // Get movements
  getMovements: async (id: number): Promise<PaletteMovement[]> => {
    const response = await apiClient.get<PaletteMovement[]>(
      API_ENDPOINTS.PALETTES.MOVEMENTS(id)
    );
    return response.data;
  },
};
