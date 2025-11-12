import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';
import {
  RFIDTag,
  RFIDTagDetail,
  RFIDTagCreate,
  RFIDTagUpdate,
  RFIDTagStatistics,
  RFIDTagListResponse,
  RFIDTagStatus,
  BulkImportResult,
} from '../../types';

export interface RFIDTagFilters {
  status?: RFIDTagStatus;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}

export const rfidTagService = {
  // List RFID tags with filters
  list: async (filters?: RFIDTagFilters): Promise<RFIDTagListResponse> => {
    const response = await apiClient.get<RFIDTagListResponse>(
      API_ENDPOINTS.RFID_TAGS.BASE,
      {
        params: filters,
      }
    );
    return response.data;
  },

  // Get RFID tag by ID
  getById: async (id: string): Promise<RFIDTagDetail> => {
    const response = await apiClient.get<RFIDTagDetail>(
      API_ENDPOINTS.RFID_TAGS.BY_ID(id)
    );
    return response.data;
  },

  // Get RFID tag by tag number
  getByNumber: async (tagNumber: string): Promise<RFIDTagDetail> => {
    const response = await apiClient.get<RFIDTagDetail>(
      API_ENDPOINTS.RFID_TAGS.BY_NUMBER(tagNumber)
    );
    return response.data;
  },

  // Create RFID tag
  create: async (data: RFIDTagCreate): Promise<RFIDTag> => {
    // Ensure data is properly formatted
    const payload: RFIDTagCreate = {
      tag_number: String(data.tag_number || '').trim(),
    };
    if (data.notes && String(data.notes).trim()) {
      payload.notes = String(data.notes).trim();
    }
    
    const response = await apiClient.post<RFIDTag>(
      API_ENDPOINTS.RFID_TAGS.BASE,
      payload
    );
    return response.data;
  },

  // Update RFID tag
  update: async (id: string, data: RFIDTagUpdate): Promise<RFIDTag> => {
    const response = await apiClient.put<RFIDTag>(
      API_ENDPOINTS.RFID_TAGS.BY_ID(id),
      data
    );
    return response.data;
  },

  // Delete RFID tag
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.RFID_TAGS.BY_ID(id));
  },

  // Mark tag as lost
  markAsLost: async (id: string, notes?: string): Promise<RFIDTag> => {
    const response = await apiClient.post<RFIDTag>(
      API_ENDPOINTS.RFID_TAGS.MARK_LOST(id),
      null,
      {
        params: { notes },
      }
    );
    return response.data;
  },

  // Mark tag as damaged
  markAsDamaged: async (id: string, notes?: string): Promise<RFIDTag> => {
    const response = await apiClient.post<RFIDTag>(
      API_ENDPOINTS.RFID_TAGS.MARK_DAMAGED(id),
      null,
      {
        params: { notes },
      }
    );
    return response.data;
  },

  // Get statistics
  getStatistics: async (): Promise<RFIDTagStatistics> => {
    const response = await apiClient.get<RFIDTagStatistics>(
      API_ENDPOINTS.RFID_TAGS.STATISTICS
    );
    return response.data;
  },

  // Bulk import from CSV
  bulkImport: async (file: File): Promise<BulkImportResult> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<BulkImportResult>(
      API_ENDPOINTS.RFID_TAGS.BULK_IMPORT,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};
