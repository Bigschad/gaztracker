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
    // S'assurer que toutes les valeurs sont des primitives
    if (response.data?.items) {
      const normalizedItems = response.data.items.map((palette): Palette => {
        const normalizedPalette: Palette = {
          ...palette,
          type: String(palette.type || '') as any,
          status: String(palette.status || '') as any,
        };
        
        if (palette.rfid_tag) {
          normalizedPalette.rfid_tag = {
            ...palette.rfid_tag,
            id: String(palette.rfid_tag.id || ''),
            tag_number: String(palette.rfid_tag.tag_number || ''),
            status: String(palette.rfid_tag.status || '') as any,
            created_by_id: String(palette.rfid_tag.created_by_id || ''),
            is_active: Boolean(palette.rfid_tag.is_active),
            notes: palette.rfid_tag.notes ? String(palette.rfid_tag.notes) : undefined,
            created_at: String(palette.rfid_tag.created_at || ''),
            updated_at: String(palette.rfid_tag.updated_at || ''),
            assigned_at: palette.rfid_tag.assigned_at ? String(palette.rfid_tag.assigned_at) : undefined,
          };
        } else {
          normalizedPalette.rfid_tag = null;
        }
        
        return normalizedPalette;
      });
      
      return {
        ...response.data,
        items: normalizedItems,
      };
    }
    return response.data;
  },

  // Get palette by ID
  getById: async (id: string): Promise<Palette> => {
    const response = await apiClient.get<Palette>(
      API_ENDPOINTS.PALETTES.BY_ID(id)
    );
    // S'assurer que toutes les valeurs sont des primitives
    const palette = response.data;
    const normalizedPalette: Palette = {
      ...palette,
      type: String(palette.type || '') as any,
      status: String(palette.status || '') as any,
    };
    
    if (palette.rfid_tag) {
      normalizedPalette.rfid_tag = {
        ...palette.rfid_tag,
        id: String(palette.rfid_tag.id || ''),
        tag_number: String(palette.rfid_tag.tag_number || ''),
        status: String(palette.rfid_tag.status || '') as any,
        created_by_id: String(palette.rfid_tag.created_by_id || ''),
        is_active: Boolean(palette.rfid_tag.is_active),
        notes: palette.rfid_tag.notes ? String(palette.rfid_tag.notes) : undefined,
        created_at: String(palette.rfid_tag.created_at || ''),
        updated_at: String(palette.rfid_tag.updated_at || ''),
        assigned_at: palette.rfid_tag.assigned_at ? String(palette.rfid_tag.assigned_at) : undefined,
      };
    }
    
    return normalizedPalette;
  },

  // Create palette
  create: async (data: PaletteCreate): Promise<Palette> => {
    const response = await apiClient.post<Palette>(
      API_ENDPOINTS.PALETTES.BASE,
      data
    );
    // S'assurer que toutes les valeurs sont des primitives
    const palette = response.data;
    const normalizedPalette: Palette = {
      ...palette,
      type: String(palette.type || '') as any,
      status: String(palette.status || '') as any,
    };
    
    if (palette.rfid_tag) {
      normalizedPalette.rfid_tag = {
        ...palette.rfid_tag,
        id: String(palette.rfid_tag.id || ''),
        tag_number: String(palette.rfid_tag.tag_number || ''),
        status: String(palette.rfid_tag.status || '') as any,
        created_by_id: String(palette.rfid_tag.created_by_id || ''),
        is_active: Boolean(palette.rfid_tag.is_active),
        notes: palette.rfid_tag.notes ? String(palette.rfid_tag.notes) : undefined,
        created_at: String(palette.rfid_tag.created_at || ''),
        updated_at: String(palette.rfid_tag.updated_at || ''),
        assigned_at: palette.rfid_tag.assigned_at ? String(palette.rfid_tag.assigned_at) : undefined,
      };
    }
    
    return normalizedPalette;
  },

  // Update palette
  update: async (id: string, data: PaletteUpdate): Promise<Palette> => {
    const response = await apiClient.put<Palette>(
      API_ENDPOINTS.PALETTES.BY_ID(id),
      data
    );
    // S'assurer que toutes les valeurs sont des primitives
    const palette = response.data;
    const normalizedPalette: Palette = {
      ...palette,
      type: String(palette.type || '') as any,
      status: String(palette.status || '') as any,
    };
    
    if (palette.rfid_tag) {
      normalizedPalette.rfid_tag = {
        ...palette.rfid_tag,
        id: String(palette.rfid_tag.id || ''),
        tag_number: String(palette.rfid_tag.tag_number || ''),
        status: String(palette.rfid_tag.status || '') as any,
        created_by_id: String(palette.rfid_tag.created_by_id || ''),
        is_active: Boolean(palette.rfid_tag.is_active),
        notes: palette.rfid_tag.notes ? String(palette.rfid_tag.notes) : undefined,
        created_at: String(palette.rfid_tag.created_at || ''),
        updated_at: String(palette.rfid_tag.updated_at || ''),
        assigned_at: palette.rfid_tag.assigned_at ? String(palette.rfid_tag.assigned_at) : undefined,
      };
    }
    
    return normalizedPalette;
  },

  // Delete palette
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.PALETTES.BY_ID(id));
  },

  // Scan palette
  scan: async (data: PaletteScan): Promise<Palette> => {
    const response = await apiClient.post<Palette>(
      API_ENDPOINTS.PALETTES.SCAN,
      data
    );
    // S'assurer que toutes les valeurs sont des primitives
    const palette = response.data;
    const normalizedPalette: Palette = {
      ...palette,
      type: String(palette.type || '') as any,
      status: String(palette.status || '') as any,
    };
    
    if (palette.rfid_tag) {
      normalizedPalette.rfid_tag = {
        ...palette.rfid_tag,
        id: String(palette.rfid_tag.id || ''),
        tag_number: String(palette.rfid_tag.tag_number || ''),
        status: String(palette.rfid_tag.status || '') as any,
        created_by_id: String(palette.rfid_tag.created_by_id || ''),
        is_active: Boolean(palette.rfid_tag.is_active),
        notes: palette.rfid_tag.notes ? String(palette.rfid_tag.notes) : undefined,
        created_at: String(palette.rfid_tag.created_at || ''),
        updated_at: String(palette.rfid_tag.updated_at || ''),
        assigned_at: palette.rfid_tag.assigned_at ? String(palette.rfid_tag.assigned_at) : undefined,
      };
    }
    
    return normalizedPalette;
  },

  // Get statistics
  getStatistics: async (): Promise<PaletteStatistics> => {
    const response = await apiClient.get<PaletteStatistics>(
      API_ENDPOINTS.PALETTES.STATISTICS
    );
    return response.data;
  },

  // Get movements
  getMovements: async (id: string): Promise<PaletteMovement[]> => {
    const response = await apiClient.get<PaletteMovement[]>(
      API_ENDPOINTS.PALETTES.MOVEMENTS(id)
    );
    return response.data;
  },
};
