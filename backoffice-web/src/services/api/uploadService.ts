import apiClient from './client';
import { API_ENDPOINTS } from '../../config/api';

interface UploadResponse {
  url: string;
  filename: string;
  original_filename: string;
  size: number;
}

export const uploadService = {
  // Upload logo
  uploadLogo: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<UploadResponse>(
      API_ENDPOINTS.UPLOADS.LOGOS,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Delete logo
  deleteLogo: async (filename: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.UPLOADS.LOGO_BY_NAME(filename));
  },

  // Get logo URL
  getLogoUrl: (filename: string): string => {
    return API_ENDPOINTS.UPLOADS.LOGO_BY_NAME(filename);
  },
};

